from urllib.request import urlretrieve
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from bokeh.plotting import figure,show

url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+employee_salaries&filename=employee_salaries&format=csv&skipfields=cartodb_id,the_geom,the_geom_webmercator'
urlretrieve(url, 'Government_Employee_Salaries.csv')
df = pd.read_csv('Government_Employee_Salaries.csv', index_col = 0)

# df = Salaries and calendar year-to-date overtime for all City employees, including elected officials and Court staff.

column_names = df.columns # Gives you the column names
df_shape = df.shape # Gives you the number of rows and columns
df_information = df.info() # Very useful = gives you a summary and column type and #values of your data
df_statistics = df.describe() # Gives you summary statistics for numerical columns

# Lets reshape our data to delete repeat values
df_pivot = df.pivot_table(index=['last_name','first_name','title','department'], columns=['calendar_year','quarter'], values=['ytd_overtime_gross', 'annual_salary'])
df_pivot = df_pivot.reset_index()

# Lets summarize the salary and OT values by year
df_pivot['2016_salary'] = df_pivot[[('annual_salary', 2016, 1), ('annual_salary', 2016, 2), ('annual_salary', 2016, 3), ('annual_salary', 2016, 4)]].mean(axis=1)
df_pivot['2017_salary'] = df_pivot[[('annual_salary', 2017, 1), ('annual_salary', 2017, 2), ('annual_salary', 2017, 3), ('annual_salary', 2017, 4)]].mean(axis=1)
df_pivot['2016_OT'] = df_pivot[[('ytd_overtime_gross', 2016, 1), ('ytd_overtime_gross', 2016, 2), ('ytd_overtime_gross', 2016, 3), ('ytd_overtime_gross', 2016, 4)]].max(axis=1)
df_pivot['2017_OT'] = df_pivot[[('ytd_overtime_gross', 2017, 1), ('ytd_overtime_gross', 2017, 2), ('ytd_overtime_gross', 2017, 3), ('ytd_overtime_gross', 2017, 4)]].max(axis=1)

df_final = df_pivot[['last_name','first_name','title','department','2016_salary','2017_salary','2016_OT','2017_OT']]
df_final.columns = ['last_name','first_name','title','department','2016_salary','2017_salary','2016_OT','2017_OT']

df_2016_salary_department = df_final.groupby('department')['2016_salary'].sum()
df_2016_salary_department = df_2016_salary_department.reset_index()
df_2016_salary_department = df_2016_salary_department.sort_values('2016_salary', ascending=False)
df_2017_salary_department = df_final.groupby('department')['2017_salary'].sum()
df_2017_salary_department = df_2017_salary_department.reset_index()
df_2017_salary_department = df_2017_salary_department.sort_values('2017_salary', ascending=False)

# Now lets plot! Is there a pattern between OT and salary??

p = figure(title = 'Salarv vs. OT')
p.circle(df_final['2016_salary'], df_final['2016_OT'], color='green', size=5, alpha=0.5)
p.circle(df_final['2017_salary'], df_final['2017_OT'], color= 'red', size=5, alpha=0.5)
# show(p)

# pd.options.display.mpl_style = 'default'

df_2016_salary_department = df_2016_salary_department.set_index('department')
df_2016_salary_department.head().plot(kind='bar', title='2016')
df_2017_salary_department = df_2017_salary_department.set_index('department')
df_2017_salary_department.head().plot(kind='bar', title='2017')
plt.show()

# Now lets look at frequency counts for categorical data (title and department)
title_counts = df.title.value_counts(dropna=False)
department_counts = df.department.value_counts(dropna=False).head(10) 

# List of unique values in a column
department_uniques = list(df.department.unique())

# Now lets visually explore our data

df['annual_salary'].plot('hist', rot=50) # x-axis = salary and y-axis = counts at each salary
plt.title('Salaries by Frequency')
plt.xlabel('Salary')
plt.show()

plt.bar(np.arange(len(department_uniques[0:10])),np.array(department_counts))
plt.xticks(np.arange(len(department_uniques[0:10])),department_uniques,rotation=90)
plt.title('Top 10 Departments by Count')
plt.xlabel('Department')
plt.ylabel('Count')
plt.show()

# I wanted to filter by year and quarter since there were repeats per quarter

df_2016_q1 = df[(df.quarter == 1) & (df.calendar_year == 2016)] 
df_2016_q2 = df[(df.quarter == 2) & (df.calendar_year == 2016)]
df_2016_q3 = df[(df.quarter == 3) & (df.calendar_year == 2016)]
df_2016_q4 = df[(df.quarter == 4) & (df.calendar_year == 2016)]
df_2017_q1 = df[(df.quarter == 1) & (df.calendar_year == 2017)] 
df_2017_q2 = df[(df.quarter == 2) & (df.calendar_year == 2017)]
df_2017_q3 = df[(df.quarter == 3) & (df.calendar_year == 2017)]
df_2017_q4 = df[(df.quarter == 4) & (df.calendar_year == 2017)]

# We can delete calendar_year and quarter from each dataset

def remove_columns(df_list, col_list):
    for each_df in df_list:
        for each_col in col_list:
            del each_df[each_col]

df_l = [df_2016_q1, df_2016_q2, df_2016_q3, df_2016_q4, df_2017_q1, df_2017_q2, df_2017_q3, df_2017_q4]
col_l = ['calendar_year', 'quarter']

remove_columns(df_l, col_l)

df_2016 = df[df.calendar_year == 2016]
df_2016 = df_2016.sort_values('annual_salary', ascending=False)
df_2017 = df[df.calendar_year == 2017]
df_2017 = df_2017.sort_values('annual_salary', ascending=False)

df_2016_group = df_2016.groupby('department')['annual_salary'].sum()
df_2016_group = df_2016_group.reset_index()
df_2016_group = df_2016_group.sort_values('annual_salary', ascending=False)

# While melting takes a set of columns and turns it into a single column, pivoting will create a new column for each unique value in a specified column.

# writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')
# df_pivot.to_excel(writer, sheet_name='Sheet1')
# writer.save()