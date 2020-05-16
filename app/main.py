import datetime
import logging
from pathlib import Path

from app.enums import TeamName
from app.handover_list import HandoverList
from app.teams import TEAMS, Team

logger = logging.getLogger("PLG")


def main(team: Team, input_file_path: Path, output_file_path: Path = None):
    # provide a default output file path to the same folder with a sensible default filename
    if output_file_path is None:
        file_ext = Path(input_file_path).suffix
        output_file_path = (
            input_file_path.parent / f"{datetime.date.today():%d-%m-%Y}_{team}".lower()
        ).with_suffix(file_ext)

    # create a HandoverList instance from the given input list
    handover_list = HandoverList(team=team, file_path=input_file_path)
    # update the list - uses live data from TrakCare
    handover_list.update()
    # save the list as a new Word document with the given output file path
    logger.debug("Saving Word document")
    handover_list.save(output_file_path)
    logger.debug("List saved at %s", output_file_path)


if __name__ == "__main__":
    team = TEAMS[TeamName.ARBAB]
    main(
        team=team, input_file_path=Path("Lists/31.12.2019.docm").resolve(), output_file_path=None,
    )
