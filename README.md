# Patient List Generator

## Example

This example runs through a simplified demonstration of what the program is capable of doing. In this scenario, it is the morning of 15/04/2020 and it is time for the list of be produced for the respiratory team.

#### The unformatted respiratory team list from the previous day (14/04/2020)

![Unformatted input list](https://github.com/mfreeborn/patient-list-generator/blob/master/images/unformatted-list-example.png?raw=true)

#### Patients under respiratory on TrakCare (morning of 15/04/2020)

* JONES, Jane 25/05/1968 7894561233 Bed 2C (reason for admission: infection ?chest)
* DARLINGTON, Mable 15/10/1935 1112223333 Bed 1B (reason for admission: ?IECOPD)

#### Newly generated output list

![Formatted and updated output list](https://github.com/mfreeborn/patient-list-generator/blob/master/images/formatted-list-example.png?raw=true)

Several things have happened:

* Mr Smith was discharged and has been removed from the list
* Mrs Darlington has been added to the list in bold, representing a new patient
* Mrs Jones has moved beds, from 1A to 2C
* Consistent formatting has been applied to each patient
* Simple formatting has been applied to the table header
* Ward-based headers have been applied to make it clearer where patients are

And now the list is accurate, up to date and visually easy to read - in a fraction of the time it would take a person to do in reality.

## Context

Currently, patient handover lists (lists) are typically produced each morning by one of the junior doctors on the team. The process involves looking at the previous day’s list and running through the following steps:

1. Removing any patients who are no longer under the care of the team (i.e. discharged, moved specialty or passed away).

2. Adding new patients to the list as they appear on TrakCare.

3. Updating existing patients (i.e.  moved bed)
Whilst not a difficult process, it can be quite time consuming to navigate through TrakCare and manually cross check all of the patients. This very manual approach is also error-prone: accidentally missing patients (especially outliers), typographical or copy and pasting errors with patient details and not noticing minor changes such as a patient moving bed, to name a few. Patients may not be seen until later in the day if they are missed off the list in the morning, and smaller errors in the list such as mistyped NHS numbers or wrong bed allocations result in a less efficient ward round.

As the generation of lists can be described in such a methodical way, it lends itself to being automated by a computer. Doing so offers several compelling advantages:

1. Speed of list generation – a computer can navigate TrakCare and process a full list of patients in a matter of seconds, compared to 15-20 minutes for a typical junior. Multiplied across the number of medical teams in the hospital and the fact that a new list needs to be generated every morning, the cumulative time and cost savings are significant.

2. Accuracy of information – the scope for human error is largely removed from the process. All rules for finding which patients belong to which team are defined in one location – within the program code. So long as these predefined rules are correct, and the information held on TrakCare itself is accurate, then the generated list will also be accurate.

3. Consistent formatting – a list with consistent formatting applied is easier to read and work with. Depending on which of the team makes the list, there can be significant variations in formatting making it slower to read and process for the rest of the team. With a predefined set of rules, this program formats lists with complete consistency.

    Patients are ordered in alphanumeric-bed order (1A, 1C, 2B, etc) and ward order. The team's "base ward" is listed first, followed by outlier wards in alphabetical order. Headings are consistently formatted throughout, and new patients are highlihted in bold. All text and horizonatally and vertically aligned, as well as being the same font and size throughout.

## How the Program Works

The program takes three inputs and produces one output. It first must be provided with the previous day’s list – this forms the basis on which new list can be produced and ensures that information about existing patients is correctly carried from one day to the next. CareFlow is the second input – this provides information regarding which patients should be present on the new list and what bed they are in. TrakCare is used by the program just to obtain the “reason for admission”.

Below is a simplified graphical representation of the inputs and outputs:

![Flow](https://github.com/mfreeborn/patient-list-generator/blob/master/images/patient-list-flow.png?raw=true)

## Usage Instructions

Upon launching the program, the user will be presented with a window into which they should enter their TrakCare and CareFlow credentials and press the `Set Credentials` button:

![Setting credentials](https://github.com/mfreeborn/patient-list-generator/blob/master/images/credentials-input-screen.png?raw=true)

Next, navigate to the `Main` tab and begin by choosing an input file (i.e yesterday's list).

If the name of the team can be inferred from the name of the input file, the team will automatically be selected, otherwise it should be selected manually from the dropdown box. The output folder will automatically be set to the same folder in which the input file is located, but can be customised. The output filename will be automatically generated as soon as the team has been selected.

![Configuring settings](https://github.com/mfreeborn/patient-list-generator/blob/master/images/list-settings.png?raw=true)
