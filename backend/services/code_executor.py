import sys
import io
from models.schemas import CodeExecutionResult

def execute_python_code(code: str) -> CodeExecutionResult:
    """
    Execute Python code and capture output.
    WARNING: This is NOT secure for production use. 
    For production, use sandboxed environments like Docker or gVisor.
    """
    
    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()
    
    sys.stdout = redirected_output
    sys.stderr = redirected_error
    
    try:
        # Execute the code
        exec(code, {"__builtins__": __builtins__})
        
        # Get the output
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
        
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        if error:
            return CodeExecutionResult(
                success=False,
                output=output,
                error=error
            )
        
        return CodeExecutionResult(
            success=True,
            output=output or "Code executed successfully (no output)",
            error=None
        )
        
    except Exception as e:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        return CodeExecutionResult(
            success=False,
            output=redirected_output.getvalue(),
            error=str(e)
        )
