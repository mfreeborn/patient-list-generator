from enums import TeamName
from handover_list import HandoverList
from teams import TEAMS, Team


def main(team: Team, input_file_path: str, output_file_path: str = None):
    if output_file_path is None:
        output_file_path = "test.docm"

    handover_list = HandoverList(team=team, file_path=input_file_path)
    handover_list.update()
    handover_list.save(output_file_path)


if __name__ == "__main__":
    team = TEAMS[TeamName.RESPIRATORY]
    main(team=team, input_file_path="31.12.2019.docm", output_file_path=None)
