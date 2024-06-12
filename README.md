![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/634ab0bb-0fc0-44cc-b648-47ff406af082)## Custom HR

This app contains this updates:

1- Add (Female Only) checkbox in Leave Type doctype, this is for leave type which is for Female gender only like (Maternity Baby) leave type
2- Add (One Time Use) checkbox in Leave Type doctype, this is for leave type which employee can apply for it just once only like (Hajj leave, Marriage Leave) leave type
3- Add (Is Annual Leave) checkbox in Leave Type doctype, this is for an annual leave type only so we can facilitate reach it in code like (Annual Leave) leave type
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/5070c25b-7971-4683-9905-0ee38d1507cd)


4- After install this app you will find new single doctype called (Leave Settings) inside HR module, under Leaves tab
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/88e8b3e7-3b0c-4f91-8b80-6bdacd8f3a4b)

5- In (Leave Settings) single doctype you will find your leave settings, please fill the fields depend on your company settings
  A. Experience Age (In Years) field is for experience age settled by the company, Employees below this age will gain 30 annual leave balance, and the employees above this age will gain 45     annual leave balance
  B. Experience Years (In Years) field is for the number of experience years, Employees who has less experience than this value will gain 30 annual leave balance, and the employees who has more than this value will gain 45 annual leave balance
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/6e091d6f-030a-4137-a3e9-86eb5e6e51c7)

6- Age of employee will calculated depends on (Date of Birth) field in (Employee) doctype to check it with (Experience Age) field inside (Leave Settings) doctype.
And employee experience will got from (Total Experience (In Years)) field inside (Employee) doctype to check it with (Experience Years) field inside (Leave Settings) doctype.
Make sure to fill them correctly!
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/3e7a9768-efbb-4561-a56a-34a278276ef8)

7- Add filter in (Leave Application) doctype to filter the deserved leave types that employee can requested
for example the leave type of (Female Only) will not been accessible by Male Employees, and they will not see the (One Time Use) leave type if they already applied for it before.
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/5728e46e-fcb4-4d78-927b-2f151aa0410e)

8- Customize (Leave Control Panel) and (Leave Policy Assignment) and add conditions to create the suitable leaves for each employee.

9- Create leave allocation using (Leave Control Panel) and (Leave Policy Assignment) will add list of employee who is not pass the conditions (age above (Experience Age) or work experience above (Experience Years)) to child table inside (Leave Settings).
![image](https://github.com/ard-omarjaber/custom_hr/assets/172369062/72d34e08-49d8-4ed2-9a01-8d8a8fff6884)

10- A daily function will work to check 25 of each month if the listed employee in (Leave Settings) passed the conditions. If any of them passed the condition then it will auto calculated the remaining months of current leave allocation of the employee and add 1.25 leave balance for each next month in the leave balance and remove its name from the list.


