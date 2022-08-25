from libraries import logger
from libraries.discord import Discord


def main():
    print("Initiating Workflow")
    try:
        email = input("Enter email:")
        username = input("Enter username:")
    except ValueError as err:
        logger.info("Something went wrong while inputting data: %s" % err)
        raise
    discord = Discord(email, username)
    try:
        discord.create_account()
    except Exception as e:
        logger.info(e)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.info("Exception in main function %s" % ex)
