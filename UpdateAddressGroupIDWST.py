import cx_Oracle
import csv
from tkinter import *

# Base Variables
old_addressID = []
carrier_type = ''
carrier_id = ''
next_bitrateid = 0
next_bitrateid_tech = []
old_tabid_tech = []
new_address_count = 0
group_id = 0
environment_is=''


# Functions
def getConnection():
    try:
        conn = cx_Oracle.connect('lionful/lfoK#jOY#10KquXr@sz4790.db.gen.local:1521/D4142T_CCH.t')
        print('Connection to WST is successful')
    except cx_Oracle.DatabaseError as e:
        raise
    return conn

def checkHouseNrExtIfNull():
    if new_address_housenumberext=='':
        return ' is null'
    else:
        str=f"='{new_address_housenumberext}'"
        return str

def getGroupid_CarrierType():
    global carrier_type, group_id
    group_id = input('Please provide group_id to insert: ')     ## Check if GroupID is Fiber or Copper
    sql_getCarrierType = f"select res_spec_id from im_hardware_group where group_id='{group_id}'"
    with con.cursor() as cur_oldCarrierCarrierKPN:
        for carrier_type_ in cur_oldCarrierCarrierKPN.execute(sql_getCarrierType):
            if carrier_type_[0]=='MAK_GRP':
                carrier_type = 'Copper'
            elif carrier_type_[0]=='VECT_GRP':
                carrier_type = 'Fiber'
            else:
                print('Error!! Unable to determine Carrier Type. Please check if Group_ID entered is correct in im_hardware_group table')

def update_im_carrier_kpn():
    global group_id, carrier_id
    try:
        with con.cursor() as cur_updateImCarrierKpn:
            sql_updateInCarrierKpn=f"update im_carrier_kpn set group_id='{group_id}' where carrier_id='{carrier_id}'"
            cur_updateImCarrierKpn.execute(sql_updateInCarrierKpn)
            print('Updated group_id in im_carrier_kpn')
    except cx_Oracle.DatabaseError as e:
        raise

def getBitrateIDForTech(technologytype):
    with con.cursor() as cur_getBitrateIDForTech:
        sql_getBitrateIDForTech=f"select bitrate_id from im_bitrate_kpn where carrier_id='{carrier_id}' and technologytype='{technologytype}'"
        for row in cur_getBitrateIDForTech.execute(sql_getBitrateIDForTech):
            return row[0]
        return None

def update_im_dp_2_tech_kpn():
    global old_tabid_tech, group_id, carrier_id
    print('Updating im_dp_2_tech_kpn')
    with con.cursor() as cur_updateDP2TechKPN:
        sql_updateDP2TechKPN = f"update IM_DP_2_TECH_KPN set group_id='{group_id}' where carrier_id='{carrier_id}'"
        try:
            print(sql_updateDP2TechKPN)
            cur_updateDP2TechKPN.execute(sql_updateDP2TechKPN)  # Update Group_id in im_dp_2_tech_kpn
            print('Updated group_id for ' + str(group_id))
        except cx_Oracle.DatabaseError as e:
            raise
    with con.cursor() as cur_updateDP2TechKPNTabID:
        for i in range(0, len(old_tabid_tech)):
            print('Value of i =' + str(i))
            try:
                sql_updateDP2TechKPNTabID = f"update IM_DP_2_TECH_KPN set tab_id='{old_tabid_tech[i][0]}' where carrier_id='{carrier_id}' and bitrate_id='{getBitrateIDForTech(old_tabid_tech[i][1])}'"
                cur_updateDP2TechKPNTabID.execute(sql_updateDP2TechKPNTabID)
                print('Updated Tab_ID for Carrier_ID '+str(carrier_id))
            except cx_Oracle.DatabaseError as e:
                raise


# Main Code
print("---------Welcome to Bulk Address Update Program---------")

# Connect to Environment
con = getConnection()

# New Address Intake
print("Taking list of addresses to configure from Address List File.")  # select address_id, post_code, house_number, house_number_ext, cp_name, carrier_id from im_house_number_kpn where group_id='92186' and tab_technologytype='GPON' and tab_status='C' and cp_nltype='NL6' fetch first 60 rows only
with open('address_id_wst.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        print(f'\t{row[0]} Address ID for post code {row[1]} and house nr {row[2]} with house nr ext {row[3]} and room {row[4]} having carrier_id {row[5]}.')
        line_count += 1
        old_addressID.append(str(row[0]))
    print(f'Processed {line_count} address nr.')
print(old_addressID)
print(len(old_addressID))
# new_address_postcode = input("Post Code: ")
# new_address_housenumber = input("House Number: ")
# new_address_housenumberext = input("House Number Ext: ")
# print(
#     "Values received: " + new_address_postcode + ", " + new_address_housenumber + ", " + new_address_housenumberext + ".")

getGroupid_CarrierType()    # Take carrier_type, group_id

# Get Tab_ID for the Group ID
print('Getting Tab_IDs from Carrier_ID_to_refer')
sql_getTabIDs = f"select tab_id,tab_technologytype from im_tech_kpn where dp_id='{group_id}'"
with con.cursor() as cur_getTabIDs:
    for fetched_tab_id in cur_getTabIDs.execute(sql_getTabIDs):
        old_tabid_tech.append((fetched_tab_id[0], fetched_tab_id[1]))

print(old_tabid_tech)

# Get Carrier ID to configure
with open('address_id_wst.csv') as csv_file:
    csv_reader=csv.reader(csv_file,delimiter=',')
    line_count=0
    for row in csv_reader:
        carrier_id=row[5]
        print('Updating im_Carrier_kpn for '+str(carrier_id))
        update_im_carrier_kpn()       # Configure im_carrier_kpn
        update_im_dp_2_tech_kpn()


# Update im_dp_2_tech_kpn
con.commit()

con.close()
