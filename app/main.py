import datetime
import logging
from pathlib import Path

from app.enums import TeamName
from app.handover_list import HandoverList
from app.teams import TEAMS, Team


def main(
    team: Team, credentials: dict, input_file_path: Path, output_file_path: Path = None
):
    if output_file_path is None:
        file_ext = Path(input_file_path).suffix
        output_file_path = (
            input_file_path.parent / f"{datetime.date.today():%d-%m-%Y}_{team}".lower()
        ).with_suffix(file_ext)

    handover_list = HandoverList(team=team, file_path=input_file_path)
    handover_list.update(credentials=credentials)
    handover_list.save(output_file_path)
    logging.debug("List updating complete")


if __name__ == "__main__":
    team = TEAMS[TeamName.ARBAB]
    main(
        team=team,
        input_file_path=Path("Lists/31.12.2019.docm").resolve(),
        output_file_path=None,
    )
