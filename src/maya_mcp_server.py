
import os
import logging
import json
import socket
import inspect
import importlib
import traceback
from enum import Enum
from typing import Sequence, List, Any, Dict, Optional, get_origin
import pprint
from itertools import chain

import mcp.server.stdio
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.fastmcp.utilities.func_metadata import func_metadata
from mcp.server.fastmcp.utilities.types import Image
from mcp.server.fastmcp.server import Context
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import pydantic_core


__version__ = "0.1.0"

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

LoggingLevel = logging.DEBUG


LOCAL_HOST = '127.0.0.1'

# Default MEL command port that Maya listens
DEFAULT_COMMAND_PORT = 50007


logging.basicConfig(
    level=LoggingLevel,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIRECTORY, 'maya_mcp_server.log')),
    ]
)

logger = logging.getLogger("MayaMCP")

_operation_manager = None


class MayaConnection:
    """ connection to the Maya instance """

    def __init__(self, host:str=LOCAL_HOST, port:int=DEFAULT_COMMAND_PORT):
        self.host = host
        self.port = port

    @staticmethod
    def _encode_python_to_mel_python(python_code:str) -> str:
        mel = python_code.replace('"', '\\"')
        mel = mel.replace('\n', '\\n')
        return f'python("{mel}")'

    @staticmethod
    def _update_script_to_capture_stdout(python_script:str) -> str:
        spaced_python_script = '    ' + python_script.replace('\n', '\n    ')
        return f"""
import io
import contextlib
_mcp_io_buf = io.StringIO()
with contextlib.redirect_stdout(_mcp_io_buf):
{spaced_python_script}
_mcp_maya_results = _mcp_io_buf.getvalue()
"""

    def _send_python_command(self, python_script:str) -> str:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))

        mel = MayaConnection._encode_python_to_mel_python(python_script)

        client.send(mel.encode('utf-8'))

        result = data = client.recv(1024)
        while len(data) == 1024:
            data = client.recv(1024)
            result += data

        if result:
            result = result.decode('utf-8')
        else:
            result = None

        client.close()

        return result


    class ScriptReturn(Enum):
        STDOUT = "stdout"
        JSON = "json"
        NONE = "none"

    def run_python_script(
        self,
        python_script:str, 
        *, 
        returns:ScriptReturn = ScriptReturn.JSON
    ):
        if returns == MayaConnection.ScriptReturn.STDOUT:
            python_script = MayaConnection._update_script_to_capture_stdout(python_script)
        else:
            python_script = "_mcp_maya_results = None\n" + python_script

        result = self._send_python_command(python_script)

        # strip any extra characters added at the end
        result = result.replace(chr(0), '')
        result = result.replace(chr(10), '')

        if returns != MayaConnection.ScriptReturn.NONE and (not result or result == '\n'):
            result = self._send_python_command("_mcp_maya_results")
            # strip any extra characters added at the end
            result = result.replace(chr(0), '')
            result = result.replace(chr(10), '')

        if returns != MayaConnection.ScriptReturn.NONE:
            try:
                result = json.loads(result)
            except:
                # if unable to parse as JSON, just return as is
                pass

        return result


class OperationsManager():
    """ manages the tools, resources and prompts """

    def __init__(self):
        self._paths = {}
        self._tools = {}

    def has_tool(self, name:str) -> bool:
        return name in self._tools

    def get_tool(self, name:str) -> Tool:
        if name in self._tools:
            return self._tools[name]
        return None

    def get_file_path(self, name:str) -> Tool:
        if name in self._paths:
            return self._paths[name]
        return None

    def get_tools(self) -> List[Tool]:
        return self._tools.values()

    def find_tools(self):
        """ find all the MCP types.Tool in the mayatools directory """
        for root, dirs, files in os.walk(os.path.join(SCRIPT_DIRECTORY, "mayatools")):
            for file in files:
                if file.endswith(".py"):
                     name, _ = os.path.splitext(file)
                     path = os.path.join(root, file)
                     tool = OperationsManager._get_function_tool(name, path)

                     if tool:
                         self._paths[name] = path
                         self._tools[name] = tool

    @staticmethod
    def _get_function_tool(maya_tool_name, filename:str) -> Tool:
        """ attempt to load a python file as a MCP types.Tool and read the function signature and docs """
        try:
            spec = importlib.util.spec_from_file_location(maya_tool_name, filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            fn = getattr(module, maya_tool_name)
        except Exception as e:
            logger.error(f"Unable to pre-load {maya_tool_name} because: {e}")
            return None

        func_doc = fn.__doc__ or ""

        is_async = inspect.iscoroutinefunction(fn)

        sig = inspect.signature(fn)
        context_kwarg = None
        for param_name, param in sig.parameters.items():
            if get_origin(param.annotation) is not None:
                continue
            if issubclass(param.annotation, Context):
                context_kwarg = param_name
                break

        func_arg_metadata = func_metadata(
            fn,
            skip_names=[context_kwarg] if context_kwarg is not None else [],
        )
        parameters = func_arg_metadata.arg_model.model_json_schema()

        tool = Tool(
            name=maya_tool_name,
            description=func_doc,
            inputSchema=parameters
        )

        return tool


def wrap_script_in_scoped_function(python_script:str, maya_tool_name:str, args:List[str]) -> str:
    spaced_python_script = '    ' + python_script.replace('\n', '\n    ')
    return f"""
def _mcp_maya_scope({','.join(args)}):
    import json
    import traceback
    from pprint import pprint
{spaced_python_script}
    try:
        results = {maya_tool_name}({','.join([a + '=' + a for a in args])})
    except Exception as e:
        # print exception to the Maya console
        traceback.print_exc()
        results = dict([('success', False), ('message', 'Error: Maya tool failed with the follow message: ' + str(e))])

    if results and not isinstance(results, str):
        try:
            results = json.dumps(results)
        except Exception as e:
            print("MayaMCP: Error attempting to return results from tool {maya_tool_name} as JSON")
            pprint(results)
            # unable to parse results as JSON, just return it
            return str(results)
            
    return results
"""


def load_maya_tool_source(
    maya_tool_name:str,
    filename:str, 
    vars:Optional[Dict[str,Any]]=None,
    *,
    log:bool = False
) -> str:
    """ load a python source file and swap in any variables """
    with open(filename, 'r') as f:
        script = f.read()

    # add in function call to the results
    results = wrap_script_in_scoped_function(script, maya_tool_name, vars.keys())
    results += f"\n_mcp_maya_results = _mcp_maya_scope("
    params = []
    for k,v in vars.items():
        if isinstance(v, str):
            params.append(f"{k}='{v}'")
        else:
            params.append(f"{k}={v}")
    results += ','.join(params)
    results += ")\n\n"

    if log:
        logger.debug(results)

    return results


def convert_to_content(
    result: Any,
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """ Convert a result to a sequence of content objects. """
    if result is None:
        return []

    if isinstance(result, TextContent | ImageContent | EmbeddedResource):
        return [result]

    if isinstance(result, Image):
        return [result.to_image_content()]

    if isinstance(result, list | tuple):
        return list(chain.from_iterable(convert_to_content(item) for item in result))  # type: ignore[reportUnknownVariableType]

    if not isinstance(result, str):
        try:
            result = json.dumps(pydantic_core.to_jsonable_python(result))
        except Exception:
            result = str(result)

    return [TextContent(type="text", text=result)]


server = Server("MayaMCP")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """ handle request from MCP client to get a list of tools """
    logger.info("Requesting a list of tools.")
    return _operation_manager.get_tools()


@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """ handle request from MCP client to call tool """

    logger.info(f"Calling tool {name} with arguments: {pprint.pformat(arguments)}")

    path = _operation_manager.get_file_path(name)
    if not path:
        error_msg = f"Tool {name} not found."
        logger.error(error_msg)
        return {"success": False, "message": error_msg}

    try:
        maya_conn = MayaConnection()
        python_script = load_maya_tool_source(name, path, arguments)
        results = maya_conn.run_python_script(python_script)
        converted_results = convert_to_content(results)
    except Exception as e:
        logger.critical(e, exc_info=True)
        error_msg = f"Error: tool {name} failed to run. Reason {e}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}

    if converted_results:
        return converted_results

    return {"success": True}


async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="MayaMCP",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == '__main__':

    _operation_manager = OperationsManager()
    _operation_manager.find_tools()

    logger.info(f"MayaMCP v{__version__} server starting up")

    import asyncio
    asyncio.run(run())

