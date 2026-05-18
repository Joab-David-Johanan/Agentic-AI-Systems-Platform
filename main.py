from research_system.tools.tool import web_search, scrape_url
from research_system.pipelines.research_pipeline import run_research_pipeline
from research_system.utils.custom_exception import CustomException
from research_system.utils.logger import get_logger

# result = web_search.invoke("what is the recent AI news in Germany?")
# print(result)

# result = run_research_pipeline("what is latest job market news in Germany?")

# output = scrape_url.invoke(
#     "https://www.dw.com/en/is-this-germanys-most-advanced-ai-factory/video-76100393"
# )
# print(output)

# smoke test for custom exception handling
# try:
#     print(1 / 0)

# except Exception as e:
#     raise CustomException("An error occurred while performing the operation.", e)

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Smoke test: logger is configured and ready")

    try:
        # This is a simple logging smoke test. It should write an INFO entry first,
        # then capture and log an exception with a traceback.
        1 / 0
    except Exception as e:
        logger.exception("Smoke test: caught an exception")
