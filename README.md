# HD Requester

![HD Requester Logo](https://github.com/mnothman/HD-Requester/blob/main/images/HD-Requester-Logo.png)

## Project Synopsis

HD Requester is a secure parts management system designed to streamline the process of checking parts in and out of a secure area. It makes it convenient for authorized personnel to access and manage parts efficiently. The application provides a user-friendly interface for tracking and monitoring parts inventory, ensuring the security and accountability of the process. Every action gets logged and provides extra information for the company owner. In the admin dashboard, the company owner can see inventory levels at a glance and also a chart that shows data for laptops, desktops, and servers. The app has a login page for the admin and everything is securely stored in an SQLite database using Argon hash algorithm.

## App Requirements

To run our app, you will need the following:
- A modern web browser
- Mouse
- Keyboard
- Monitor
- [SQLite](https://www.sqlite.org/download.html)
- [Python](https://www.python.org/downloads)
- Flask
    - Run the command `pip install flask` to install Flask.

## Directions to Launch the App

Follow these steps to launch the app on your local computer:

1. Clone the repository to your local machine.
1. Open your terminal or command prompt.
1. Navigate to the directory where the app is located using the 'cd' command.
1. Run the command `python ./app.py` to start the app.
1. Open your web browser and go to `http://localhost:5000`.
1. You should now see the app running in your browser.

Note: Make sure you have SQLite, Python, and Flask installed before following those steps.

## Testing

*This section will be used in CSC 191 to outline the testing procedures and guidelines for the HD Requester application.*

## Deployment

*This section will be used in CSC 191 to provide instructions and best practices for deploying the HD Requester application in a production environment.*

## Developer Instructions

*This section will be used in CSC 191 to document the development workflow, coding standards, and guidelines for contributing to the HD Requester project.*

## Timeline

The following is a timeline of key milestones for the HD Requester project, based on the user stories created in the backlog for all the key features with estimates:

![Jira Timeline](https://github.com/mnothman/HD-Requester/blob/main/images/jira-timeline.png)

*Note: The timeline is subject to change based on the progress and any unforeseen challenges encountered during the development process.*
| Date          | Information                                                                   |
|---------------|-----------------------------------------------------------------------------------|
| Feb 26, 2024  | Research HTML frameworks and programming languages                                 |
| Mar 04, 2024  | Create Mockup and app flow.                                                        |
| Mar 04, 2024  | Decided on Python with Flask, SQLite, and Bootstrap.                                 |
| Mar 04, 2024  | Created basic homepage.                                                             |
| Mar 11, 2024  | Started working on Modal feature.                                                   |
| Mar 24, 2024  | Parse text into local variables.                                                    |
| Mar 24, 2024  | Make the homepage table show data from the DB.                                       |
| Mar 24, 2024  | Manually add to inventory working.                                                  |
| Apr 08, 2024  | Switch from static HTML to AJAX                                                      |
| Apr 17, 2024  | Sort data, include knowing that Gigabyte is less than Terabyte                       |
| Apr 21, 2024  | Modal function with parameters created                                               |
| Apr 24, 2024  | Live search working                                                                  |
| Apr 25, 2024  | Manually remove to inventory working.                                                |
| Apr 26, 2024  | Check-in / Check-out buttons get JavaScript to know what is selected.               |
| Apr 26, 2024  | Check-in / Check-out buttons using text area.                                        |

| Date          | Information                                                                   |
|---------------|-----------------------------------------------------------------------------------|
| Sep 09, 2024  | Create Windows Command Prompt script to install Python, Flask and SQLite           |
| Sep 09, 2024  | Create Windows Command Prompt script to uninstall Pythin, Flask, SQLite, and any configuration files in Windows. |
| Sep 09, 2024  | Find edge cases when parsing the text and handle those errors.                     |
| Sep 09, 2024  | Implement search to work with sort.                                                 |
| Sep 23, 2024  | Sanitize SQL statements for extra security.                                         |
| Sep 23, 2024  | Create static HTML of Admin Dashboard basic layout as it appears in the mockup.     |
| Oct 07, 2024  | Create dynamic Admin Dashboard, pulling data from the DB. Have the chart switch when selecting a month in the list |
| Oct 07, 2024  | Implement search in Admin Dashboard.                                                |
| Oct 21, 2024  | Implement Admin login from previously made HTML from Sprint 1. Connect it to the admin table in DB |
| Oct 21, 2024  | Implement Admin password recovery from previously made HTML from Sprint 1. Connect it to the admin table in DB |
| Nov 04, 2024  | Encrypt the password and security answers in the database.                          |


## Entity-Relationship Diagram (ERD)

![ERD](https://github.com/mnothman/HD-Requester/blob/main/images/ER-DiagramHD_Requester.png)

The above ERD represents the database schema and relationships between entities in the HD Requester application.

## Team Roster

- Mohammad Othman
- Kaylyn Saludo
- Richard Clinger
- Juan Valentin Mendez
- Hamza Kassem
- Salvador Del Rio Torres
- Abdul Karim Nushin
- Delia Nepomuseno Hernandez

## TEAM REFRESH

![Additional Logo](https://github.com/mnothman/HD-Requester/blob/main/images/refresh-icon.png)



