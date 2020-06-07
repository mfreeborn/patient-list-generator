import datetime
import logging

from .. import settings
from .models import HandoverList

logger = logging.getLogger()


def generate_list(team, input_file, input_filename):
    """Produce an updated and formatted handover list.

    This is the main function which produces an updated patient handover
    list. A list is first created from the input_file, before it is updated
    by gathering fresh data from TrakCare.

    The handover list is saved at a dynamic location; the user provides the path
    to a base folder of handover lists, with the rest of the path being a function
    of the team name and current date.

    Args:
        team (Team): An instance of Team, representing which medical team we
            want to make an updated list for. Includes information such as
            the team's base ward as well as which consultants belong to the team.
        input_file (io.BytesIO): A file-like object; the team's previous handover
            list upon which to build the updated list.
        input_filename (Path): The filename pertaining to the input name.

    Returns:
        Path: The path to the newly updated handover list.

    """
    # create a default output file path. Using the file extension provided by the
    # input_filename avoids making assumptions about whether it is a DOCM or DOCX
    # file
    today = datetime.date.today()
    file_ext = input_filename.suffix
    output_file_path = (
        settings.LIST_ROOT_DIR
        / f"{team.name}"
        / f"{today:%Y}"
        / f"{today:%m %B}"
        / f"{today:%d-%m-%Y}_{team.name}".lower()
    ).with_suffix(file_ext)
    # ensure the folder exists
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("Using the following output file path: %s", output_file_path)

    # create a HandoverList instance from the given input list
    logger.debug("Creating HandoverList instance from the input file")
    handover_list = HandoverList(team=team, file=input_file, filename=input_filename)
    # update the list - uses live data from TrakCare
    logger.debug("Updating the base handover list")
    handover_list.update()
    # save the list as a new Word document with the given output file path
    logger.debug("Saving the updated handover list")
    handover_list.save(output_file_path)
    logger.debug("List saved at %s", output_file_path)
    return output_file_path
