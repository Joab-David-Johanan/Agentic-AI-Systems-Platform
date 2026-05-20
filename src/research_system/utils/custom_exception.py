import sys


class CustomException(Exception):
    """Custom exception class for handling specific errors in the research system."""

    def __init__(self, message, error_detail: Exception | None = None):
        self.error_message = self.get_detailed_error_message(message, error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def get_detailed_error_message(message, error_detail: Exception | None) -> str:
        """Constructs a detailed error message including the original message and error details."""
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown"
        line_number = exc_tb.tb_lineno if exc_tb else "Unknown"
        error_message = f"{message} | File: {file_name} | Line: {line_number}"
        if error_detail:
            error_message += f" | Error Detail: {str(error_detail)}"
        return error_message

    def __str__(self):
        return f"CustomException: {self.error_message}"
