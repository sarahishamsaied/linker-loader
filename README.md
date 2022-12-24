# Absolute Linker & Loader

## Table of Content

1 - [Quick Overview](#overview). 

2 - [Installation Guide](#installation-guide).

3 - [How to Launch](#how-to-launch).

4 - [Sample Run](#sample-run).





# Overview

This software’s purpose is to generate an Absolute Loader for **SIC HTE** record, and a Linker-Loader **HDRTME** record with an external symbol table.
Depending on the user's preferences, an absolute loader or an absolutelinker can be generated.Basically, the project consists of two main parts

| SIC                                                                                | SIC/XE                                                                                                         |
|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| A user should import the HTE REC from their PC                                     | A user can import the HDRTME REC from their PC                                                                 |
| The user should see the simulated SIC memory pop-up filled with the correct values | The user should see the simulated SIC/XE memory pop-up window  filled with the correct values & modifications  |
|                                                                                    | The user should be prompted to enter the address at which the memory will begin filling the gaps               |
|                                                                                    | The user can see the generated external symbol table whether in  a .txt file or as a graphical user  interface |



# Installation Guide

Project Installation
1 - Open the CMD

2 - Navigate to the desired installation path.

3 - Then write:

      git clone https://github.com/sarahishamsaied/linker-loader
      cd linker-loader
      pip install numpy
      pip install pandas
      pip install tkinter
      pip install pandastable
      
 ## Sample Run
 
  ## Starting Menu

![unnamed (2)](https://user-images.githubusercontent.com/71923204/209451210-2d657946-06a5-476d-ad13-4c1553090351.png)
 
 
 ## Absolute Loader
 
 ![unnamed](https://user-images.githubusercontent.com/71923204/209451046-9e6b88a6-df96-4236-b0cc-26cdffdb6a5d.png)
 
 # SIC/XE
 
![unnamed (1)](https://user-images.githubusercontent.com/71923204/209451199-af567326-fb3a-4b83-a414-caad6b4d7cde.png)



![unnamed (3)](https://user-images.githubusercontent.com/71923204/209451219-259b6ab2-be03-4a28-9622-1c798cb2cdc6.png)

## External Symbol Table


![unnamed (4)](https://user-images.githubusercontent.com/71923204/209451225-ad7c9e91-a9b2-42b4-aa77-c41b2ffffb7c.png)

## Linker 

![unnamed (5)](https://user-images.githubusercontent.com/71923204/209451227-090fcc14-ea8c-426c-9180-7f2af7e43d32.png)




