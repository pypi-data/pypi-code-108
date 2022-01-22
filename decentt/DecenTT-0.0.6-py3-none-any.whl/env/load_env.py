def load_env(path: str) -> None:
    from dotenv import load_dotenv
    from tqdm import tqdm
    from DecenTT.env.logger import logger

    try:
        try:
            logger.info("Loading Environment Variables")
            for i in tqdm(range(100)):
                pass
        except Exception as e:
            logger.debug("Error in TQDM, kindly check the package")
        load_dotenv(path)
        logger.info("Environment Variables Loaded")

    except Exception as e:
        logger.error("Error in loading Environment Variables")
        logger.error(str(e))
