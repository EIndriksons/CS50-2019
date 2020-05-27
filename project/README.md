# Harvard CS50 - Final Project - ScoutFin

ScoutFin is a web application built in Flask to help manage a small company or NGO business expenses towards its employees. It provides an efficient workflow that allows the user (employee) to register and submit work-related expenses which then are reviewed, accepted, or denied by the admin (manager).

See build log in Trello: [www.trello.com/dev-cs50-project-finance](https://trello.com/b/WC3h0emA/dev-cs50-project-finance)

## Features Include:
- **Efficient Workflow** - The user is guided to create a business expense form in which he adds expense transactions and fills in all of the necessary fields. The form then gets submitted for review by the admins, who can adjust, correct, and fill in the remaining information giving their final decision to either accept or reject the expense form. This is achieved through a list of form and individual transaction statuses beginning from "Draft" all the way to the final status of "Accepted", "Paid" or "Denied".
- **Registration Whitelist** - Because this is designed for small organizations, new users must be accepted by the admins to give them access to the system in order to prevent spam or malicious use.
- **User Roles** - System supports two user roles - the normal user who can submit his own business expense forms and admin users who can also review other user expense forms, access admin dashboards, registration whitelist, and admin (site-wide) settings.
- **User Settings** - To submit a valid business expense form we have to collect such information as the user's government issued personal code and bank account details. This is not part of the registration process because the intent is for the user to get whitelisted and guided through this process through the business form.
  * **Bank Account support** - The settings support adding more than one bank account details, in case the user wishes to be paid in any one of his personal accounts. The bank accounts go through the client and server-side validation process to make sure that they are legitimate and the user has not made any mistakes.
  * **Password Change** - The user can change his password anytime.
- **Database Eventlog** - Because we are working with important financial data that in some jurisdictions must be kept for several years, we must ensure that no data is lost or accidentally deleted. For this reason, the system offers event log functionality through database triggers that track every update and deletion event in a separate table. This also enables for future data analysis.

## Workflow Use Case:
1. **Registration** - User registers and is redirected to the whitelist page. As he is not whitelisted he has only access to his settings, where he is encouraged to enter personal code and bank details to make the next steps more efficient.
2. **Whitelist** - Admin notices a new registration and can choose to "Accept" or "Deny" this user in the admin 'Registration' dashboard.
3. **Business Expense Form** - After the user is accepted, he can go to the 'Finance' tab and 'Create New Form'.
   1. The empty form has status "Draft" and the user has to fill in the basic information, such as the date, description, and add at least one transaction. Afterward, the user can 'Submit for Review' the form, which then takes the status of "New".
      1. The transaction also has status "Draft" and the user has to fill in the date, partner, document type, document number, expense description, and the amount. Afterward, the user can 'Submit' the transaction, after which it takes the status of "New".
   2. After submitting the form for review the user cannot change any information or delete the form unless he 'Unsubmits' it. During this process, if the user has not set his personal code or bank account details in the settings - submission is not possible unless it is done.
   3. After submission, the form appears in the Admins dashboard, which holds the forms in statuses "New", "Review" and "Accepted".
4. **Review Process** - Admin notices the new expense form in the Admins dashboard. Opens it for review and presses 'Assign To Me' indicating that he as an admin user will take over the form for review. The status of the form and its transaction then changes to "Review".
   1. Admin has to make sure that the information is correct, assign a 'Number' for the whole expense form, and review each of the transactions.
   2. During transaction review, the admin has to make sure that the information is correct and input the 'Accepted' expense amount (in case the full sum is not eligible). If the accepted sum is 0.00, the transaction takes the status of "Denied" and if it is > 0.00 the status of "Accepted".
   3. After each transaction is reviewed and its status is either "Accepted" or "Denied" the whole expense form can also be "Accepted" or "Denied".
      1. If the form is "Accepted", and the money is reimbursed in real life, the status can then be changed to "Paid".

## Setup:
Setup is very simple and only requires the creation of a database with the respective tables and triggers. This is done by running the **[setup.py](/project/setup.py)** file which creates "project.db" file in the project location.

Admin user access is given through a manual database UPDATE by changing User 'role' to 'Admin' and 'status' to 'Accepted'. Otherwise, the registration process works as intended.