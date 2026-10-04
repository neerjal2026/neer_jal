# Neer Jal

**Driver trip tracking and employee operations for a purified-water business.** Neer Jal is an installable mobile PWA backed by Frappe and built with Vue 3 and Frappe UI.

## Trip Tracking

Drivers sign in with an Employee login assigned the **Driver** role (mapped to Frappe's existing **Sales User** role). A driver starts a trip by selecting a vehicle and trip route, entering the starting odometer reading, and optionally adding notes. The logged-in driver is assigned automatically.

When the trip closes, the driver enters the ending odometer reading. The app calculates distance travelled and records the route price as driver credit. Each completed trip creates one linked Driver Credit entry. Managers maintain route names and prices and can view the driver Trip Sheet, filter by date and driver, and export it as PDF.

## Employees and HR

Employee records can create Driver and Office Staff logins. Employee profiles include employment, address, and bank information.

- **Time Clock** supports clock-in and clock-out, including shifts crossing midnight.
- **Payroll** calculates pay for a selected date range and can export employee payslips as PDF.
- **Salary Advances** tracks employee advances.

## Roles

| Role | Access |
|---|---|
| **Sales Manager** | Trip routes, all trips, vehicles, employees, Trip Sheet reports, and HR tools |
| **Sales User** | Start and close own trips, view own trip history |
| **Office Staff** | Time Clock, Salary Advances, and Payroll |
| **System Manager** | Full system access |

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/neerjal2026/neer_jal.git --branch main
bench --site <site-name> install-app neer_jal
```

After updating an existing site, run `bench --site <site-name> migrate` to apply DocType changes and remove the retired customer, delivery, payment, driver-master, and SMS settings DocTypes and their records.
