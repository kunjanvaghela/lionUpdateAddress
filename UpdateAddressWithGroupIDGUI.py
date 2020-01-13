import cx_Oracle
import csv
from tkinter import *

mainWindow=Tk()
mainWindow.title('Update')
mainWindow.geometry('400x300')

# Base Variables
old_addressID = ""
new_address_postcode = ""
new_address_housenumber = ""
new_address_housenumberext = ""
address_exists = 'N'
carrier_id_to_refer = ''
carrier_type = ''
carrier_id = ''
next_bitrateid = 0
next_bitrateid_tech = []
old_tabid_tech = []
new_address_count = 0
group_id = 0
groupid_or_carrierid=''
im_cp_id_created=''
existsInImCP=''
con=None
txtstatusLbl=StringVar()
txtstatusLbl.set('Starting the Program!')

# GUI Variables


# Functions
def getNewBitrateFromTech(i):
    for j in range(0, len(next_bitrateid_tech)):
        if next_bitrateid_tech[j][1]==i:
            return next_bitrateid_tech[j][0]

def getConnection():
    print(str(environment_is.get()))
    global con
    try:
        if environment_is.get()==1:
            conn = cx_Oracle.connect('lionful/K8Uth6$dR21Qe9LfDS@sz4534.db.gen.local:1521/D4033A_CCA.a')
            print('Connection to CT1 is successful')
            txtstatusLbl.set('Connected to CT1 successfully, please enter Address details')
            con=conn
        elif environment_is.get() == 2:
            conn = cx_Oracle.connect('lionful/lfoK#jOY#10KquXr@sz4790.db.gen.local:1521/D4142T_CCH.t')
            print('Connection to WST is successful')
            txtstatusLbl.set('Connected to WST successfully, please enter Address details')
            con=conn
        elif environment_is.get()==3:
            conn = cx_Oracle.connect('lionful/lfoK#jOY#14SquXr@sz4906.db.gen.local:1521/D4158A_CCA.a')
            print('Connection to CT2 is successful')
            txtstatusLbl.set('Connected to CT2 successfully, please enter Address details')
            con=conn
        else:
            print('Error! Cant find correct environment details entered.')
    except cx_Oracle.DatabaseError as e:
        raise

def getOldAddress():
    with con.cursor() as cur_getOldAddr:
        sql_findAddressToReplace = "select address_id, post_code, house_number, house_number_ext from im_house_number_kpn where group_id is null and cp_nonwaddress='non-network' and tab_technologytype is null and cp_name is null and cp_type='ISRA' and house_number_ext is null fetch first 10 rows only"
        for row in cur_getOldAddr.execute(sql_findAddressToReplace):
            print("Do you want to change Address_ID : " + str(row[0]) + " and address: " + str(row[1]) + ", " + str(row[2]) + ", " + str(row[3]))
            if input("Change? [Y]:  ") == 'Y':
                old_addressID = row[0]
                break
            else:
                continue

def fetchNextBitrate():
    sql_fetchNextBitrate = 'select S_IM_BITRATE_ID.nextval from dual'  # AVDB_BIT, S_IM_BITRATE_ID
    with con.cursor() as cur_fetchNextBitrate:
        for row in cur_fetchNextBitrate.execute(sql_fetchNextBitrate):
            global next_bitrateid
            next_bitrateid = int(row[0])
    return next_bitrateid

def fetchNextCPID():
    sql_fetchNextCPID = 'select S_IM_CP_ID.nextval from dual'
    with con.cursor() as cur_fetchNextCPID:
        for row in cur_fetchNextCPID.execute(sql_fetchNextCPID):
            global im_cp_id_created
            im_cp_id_created = int(row[0])

def fetchNextCarrierID():
    sql_fetchNextCarrierID = 'select S_IM_CARRIER_ID.nextval from dual'
    with con.cursor() as cur_fetchNextCarrierID:
        for row in cur_fetchNextCarrierID.execute(sql_fetchNextCarrierID):
            global carrier_id
            carrier_id = int(row[0])

def checkHouseNrExtIfNull():
    if new_address_housenumberext=='':
        return ' is null'
    else:
        str=f"='{new_address_housenumberext}'"
        return str

def checkIfGroupIDOk():
    global carrier_type, group_id
    global next_bitrateid_tech, old_tabid_tech, next_bitrateid, carrier_id, carrier_type
    file_name=''
    countOfTechInBitSample = 0
    countOfTechInIMTechtable = 0
    if carrier_type=='Fiber':
        file_name='bitrate_fiber.csv'
    elif carrier_type=='Copper':
        file_name='bitrate_copper.csv'
    else:
        input('Carrier_type incorrect to fetch file to update bitrate')
        exit()
    with open(file_name) as csv_file:
        csv_reader=csv.reader(csv_file,delimiter=',')
        for row in csv_reader:
            countOfTechInBitSample=countOfTechInBitSample+1
    with con.cursor() as cur_countTechInGroupID:
        sql_getTechCountInImTechKPN=f"select * from im_tech_kpn where dp_id='{group_id}'"
        try:
            for countTechInGroupID in cur_countTechInGroupID.execute(sql_getTechCountInImTechKPN):
                countOfTechInIMTechtable=countOfTechInIMTechtable+1
        except cx_Oracle.DatabaseError as e:
            raise
    print('countOfTechInBitSample = '+str(countOfTechInBitSample))
    print('countOfTechInIMTechtable = ' + str(countOfTechInIMTechtable))
    if countOfTechInIMTechtable==countOfTechInBitSample:
        print('Group ID has same number of technology as bitrate file available')
    else:
        print('No of Technology does not match with the sample bitrate file. Either update Group ID in im_Tech_kpn or provide correct Group ID')
        input('Exiting')
        exit()


def getGroupid_CarrierType():
    global carrier_type, group_id
    carrierGroupIDFound = 0
    group_id = input('Please provide group_id to insert: ')     ## Check if GroupID is Fiber or Copper
    sql_getCarrierType = f"select res_spec_id from im_hardware_group where group_id='{group_id}'"
    with con.cursor() as cur_oldCarrierCarrierKPN:
        for carrier_type_ in cur_oldCarrierCarrierKPN.execute(sql_getCarrierType):
            carrierGroupIDFound = 1
            if carrier_type_[0]=='MAK_GRP':
                carrier_type = 'Fiber'
            elif carrier_type_[0]=='VECT_GRP':
                carrier_type = 'Copper'
            else:
                input('Error!! Unable to determine Carrier Type. Please check if Group_ID entered is correct in im_hardware_group table')
                exit()
            print('Carrier_Type found: ' + carrier_type)
    if carrierGroupIDFound == 0:
        input('Error!! Group ID entered does not exist in the environment. Exiting the program.')
        exit()
    checkIfGroupIDOk()

def update_im_cp_kpn():
    global carrier_type, existsInImCP, im_cp_id_created
    sql_checkImCpKpnExists=f"select cp_id, cp_name, cp_type, cp_nonwaddress from im_cp_kpn where address_id='{old_addressID}'"
    with con.cursor() as cur_checkImCpKpnExists:
        for checkImCpKpnExists in cur_checkImCpKpnExists.execute(sql_checkImCpKpnExists):
            if carrier_type=='Copper' and checkImCpKpnExists[2]=='ISRA':
                existsInImCP='Y'
                im_cp_id_created=checkImCpKpnExists[0]
                print('ISRA CP exists in im_cp_kpn table. Will check now if non-network or not.')
                if checkImCpKpnExists[1]==None and checkImCpKpnExists[2]=='ISRA' and checkImCpKpnExists[3]=='non-network':                 # Check if Non-Network, correct Non-Network
                    print('Updating im_cp_kpn for Copper non-network addresss')
                    try:
                        with con.cursor() as cur_updateImCpKpnNonNW:
                            sql_updateImCpKpnNonNW=f"update im_cp_kpn set cp_name='001', cp_nonwaddress='network' where cp_id='{checkImCpKpnExists[0]}'"
                            cur_updateImCpKpnNonNW.execute(sql_updateImCpKpnNonNW)
                            print('Updated im_cp_kpn address to network')
                    except cx_Oracle.DatabaseError as e:
                        raise
                else:
                    print('ISRA CP seems Okay, using existing one, that is cp_id:  '+str(checkImCpKpnExists[0]))
            elif carrier_type=='Fiber' and checkImCpKpnExists[2]=='Room':
                existsInImCP='Y'
                im_cp_id_created=checkImCpKpnExists[0]
                print('Room CP exists in im_cp_kpn table.')
    if existsInImCP=='':
        input('No entry in im_cp_kpn for the carrier_type of Group_id. Press any key to create entry now in im_cp_kpn')
        fetchNextCPID()
        sql_insertInImCpKPN=''
        if carrier_type=='Copper':
            sql_insertInImCpKPN=f"insert into im_cp_kpn values ({im_cp_id_created},{old_addressID},'EN','001','ISRA',NULL,NULL,NULL,'DQS',NULL,'0','2','network','5',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,SYSDATE,NULL)"      # cp_id sequence: S_IM_CP_ID
        elif carrier_type=='Fiber':
            sql_insertInImCpKPN=f"insert into im_cp_kpn values ({im_cp_id_created},{old_addressID},'EN',NULL,'Room','NL6','FTU_GN02',NULL,'Reggefiber',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Fiber afgewerkt op FTU en doorgemeten','2',NULL,NULL,NULL,NULL,SYSDATE,NULL)"
        try:
            with con.cursor() as cur_insertImCpKpn:
                cur_insertImCpKpn.execute(sql_insertInImCpKPN)
                print('Inserted in IM_CP_KPN successfully.')
        except cx_Oracle.DatabaseError as e:
            raise

def update_im_carrier_kpn():
    global old_addressID, im_cp_id_created, carrier_id, group_id, existsInImCP
    if existsInImCP=='Y':
        # Get Carrier ID to configure
        sql_getCarrierID = f"select * from im_carrier_kpn where address_id='{old_addressID}' and carrier_type='{carrier_type}' and carrier_serviceid is null and (group_id='-9' or group_id is null)"
        with con.cursor() as cur_getCarrierKPNInfo:
            for carrier_type_ in cur_getCarrierKPNInfo.execute(sql_getCarrierID):
                print('Retrieved Carrier_ID from im_carrier_kpn')
                carrier_id = carrier_type_[0]
        if carrier_id == '':
            input('Carrier_ID was not updated from im_carrier_kpn for Address to Configure, Program will add new carrier_id with cp_id derived, cp_id: '+str(im_cp_id_created))
            insert_im_carrier_kpn()
        try:
            with con.cursor() as cur_updateImCarrierKpn:
                sql_updateInCarrierKpn=f"update im_carrier_kpn set group_id='{group_id}' where carrier_id='{carrier_id}'"
                cur_updateImCarrierKpn.execute(sql_updateInCarrierKpn)
                print('Updated group_id in im_carrier_kpn')
        except cx_Oracle.DatabaseError as e:
            raise
    else:
        insert_im_carrier_kpn()

def insert_im_carrier_kpn():
    global old_addressID, im_cp_id_created, carrier_id, group_id, existsInImCP
    fetchNextCarrierID()
    if carrier_type=='Fiber':
        sql_insertInImCarrierKPN=f"insert into im_carrier_kpn values ({carrier_id},null,{im_cp_id_created},{group_id},null,null,{old_addressID},'EN','Fiber',null,'3002',null,null,null,'Reggefiber','REGG',null,SYSDATE,null,sysdate,null)"
    elif carrier_type=='Copper':
        sql_insertInImCarrierKPN=f"insert into im_carrier_kpn values ({carrier_id},null,{im_cp_id_created},{group_id},null,null,{old_addressID},'EN','Copper',null,null,null,null,null,'DQS','MDF',null,null,'MAN-CREATED',sysdate,null)"
    else:
        input('Something went wrong. No Carrier_Type determined. Press any key to exit the program. Analyze!!')
        exit()
    with con.cursor() as cur_insertImCarrierKpn:
        try:
            cur_insertImCarrierKpn.execute(sql_insertInImCarrierKPN)
            print('Inserted new row in im_carrier_kpn with carrier_id: '+str(carrier_id))
        except cx_Oracle.DatabaseError as e:
            raise


def update_im_bitrate_kpn_from_file():
    global next_bitrateid_tech, old_tabid_tech, next_bitrateid, carrier_id, carrier_type
    file_name=''
    if carrier_type=='Fiber':
        file_name='bitrate_fiber.csv'
    elif carrier_type=='Copper':
        file_name='bitrate_copper.csv'
    else:
        input('Carrier_type incorrect to fetch file to update bitrate')
        exit()
    with open(file_name) as csv_file:
        csv_reader=csv.reader(csv_file,delimiter=',')
        for row in csv_reader:
            next_bitrateid_tech.append((fetchNextBitrate(), row[14]))
            sql_insertBitrateKPN = f"insert into im_bitrate_kpn values ('{next_bitrateid}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}','{row[7]}','{row[8]}','{row[9]}','{row[10]}','{row[11]}','{row[12]}','{carrier_id}','{row[14]}',NULL,NULL)"
            try:
                print(sql_insertBitrateKPN)
                with con.cursor() as cur_insertBitrateKPN:
                    cur_insertBitrateKPN.execute(sql_insertBitrateKPN)
                    print('Inserted 1 Row')
            except cx_Oracle.DatabaseError as e:
                raise

    sql_getOldBitrateInfo = f"select * from im_bitrate_kpn where carrier_id='{carrier_id_to_refer}'"
    with con.cursor() as cur_oldBitrateInfo:
        for old_bitrate_info in cur_oldBitrateInfo.execute(sql_getOldBitrateInfo):
            next_bitrateid_tech.append((fetchNextBitrate(), old_bitrate_info[14]))
            sql_insertBitrateKPN = f"insert into im_bitrate_kpn values ('{next_bitrateid}','{old_bitrate_info[1]}','{old_bitrate_info[2]}','{old_bitrate_info[3]}','{old_bitrate_info[4]}','{old_bitrate_info[5]}','{old_bitrate_info[6]}','{old_bitrate_info[7]}','{old_bitrate_info[8]}','{old_bitrate_info[9]}','{old_bitrate_info[10]}','{old_bitrate_info[11]}','{old_bitrate_info[12]}','{carrier_id}','{old_bitrate_info[14]}',NULL,NULL)"
            try:
                print(sql_insertBitrateKPN)
                with con.cursor() as cur_insertBitrateKPN:
                    cur_insertBitrateKPN.execute(sql_insertBitrateKPN)
                    print('Inserted 1 Row')
            except cx_Oracle.DatabaseError as e:
                raise

def checkIfAddInAvDb():
    global new_address_postcode, new_address_housenumber, new_address_housenumberext, new_address_count
    new_address_postcode=txtPostCodeEnter.get()
    new_address_housenumber=txtHouseNrEnter.get()
    new_address_housenumberext=txtHouseNrExtEnter.get()
    sql_checkAddressAvDb = f"select * from im_address_ext where addr_name1='{new_address_postcode}' and addr_name2='{new_address_housenumber}' and addr_name3{checkHouseNrExtIfNull()}"
    print(sql_checkAddressAvDb)  # Check query
    with con.cursor() as cur_validateAddress:
        for countAvDb in cur_validateAddress.execute(sql_checkAddressAvDb):
            new_address_count = cur_validateAddress.rowcount
            print('Number of entries for Address in im_address_ext = '+str(new_address_count))
            txtstatusLbl.set('Number of entries for Address in im_address_ext = '+str(new_address_count))
        if new_address_count == 1:
            address_exists = 'Y'
            old_addressID = countAvDb[0]
            print('Existing Address ID against below address: ' + str(old_addressID))
            txtstatusLbl.set('Existing Address ID against below address: ' + str(old_addressID))
        elif new_address_count > 1:
            input('Multiple Address IDs found against the given address. Please check, correct the data.')
            txtstatusLbl.set('Error.. Check!!')
            exit()
        else:
            old_addressID = input('Address does not exist in im_address_ext. Please provide Address_ID to replace: ')
            getOldAddress()

def resetConnectionRadioBtn():
    radCT1.deselect()
    radCT2.deselect()
    radWST.deselect()

# Main Code


frameHeader=Frame(mainWindow,relief=RAISED, borderwidth=1)
frameHeader.pack(fill=BOTH,side=TOP)
lblTitle=Label(frameHeader,text='Welcome to the Program!')
lblTitle.grid(row='0')

frameStatus=Frame(mainWindow,relief=RAISED, borderwidth=1)
frameStatus.pack(fill=BOTH,side=BOTTOM)
lblStatus=Label(frameStatus,textvariable=txtstatusLbl)
lblStatus.pack(fill=BOTH)

frameGetConnection=Frame(mainWindow,relief=RAISED, borderwidth=1)
frameGetConnection.pack(side=LEFT,expand=0,fill=BOTH)
environment_is=IntVar()
lblChooseConn=Label(frameGetConnection,text='Please select environment: ')
lblChooseConn.grid(row='0')
radCT1=Radiobutton(frameGetConnection,text='CT1',value=1, variable=environment_is).grid(row='1',column='0')
radWST=Radiobutton(frameGetConnection,text='WST',value=2, variable=environment_is).grid(row='2',column='0')
radCT2=Radiobutton(frameGetConnection,text='CT2',value=3, variable=environment_is).grid(row='3',column='0')
btnGetConnection=Button(frameGetConnection,text='Environment Selected', command=getConnection).grid(row='4',column='0')
txtstatusLbl.set('First connect to an environment')
#resetConnectionRadioBtn()

frameGetAddress=Frame(mainWindow,relief=RAISED, borderwidth=1)
frameGetAddress.pack(side=LEFT,expand=TRUE,fill=BOTH)

lblAddressEnter=Label(frameGetAddress,text='Please enter address :').grid(row='1')
lblPostCodeEnter=Label(frameGetAddress,text='Post Code:').grid(row='2',column='0')
txtPostCodeEnter=Entry(frameGetAddress,width='8')
txtPostCodeEnter.grid(row='2',column='1')
lblHouseNrEnter=Label(frameGetAddress,text='House Nr:').grid(row='3',column='0')
txtHouseNrEnter=Entry(frameGetAddress,width='6')
txtHouseNrEnter.grid(row='3',column='1')
lblHouseNrExtEnter=Label(frameGetAddress,text='House Nr Ext:').grid(row='4',column='0')
txtHouseNrExtEnter=Entry(frameGetAddress,width='6')
txtHouseNrExtEnter.grid(row='4',column='1')
btnAddressCheck=Button(frameGetAddress,text='Check Address',command=checkIfAddInAvDb).grid(row='5',column='1')

mainWindow.mainloop()
# print("---------Welcome to Address Update Program---------")
#
# # Get Environment to connect
# while not (environment_is=='1' or environment_is=='2' or environment_is=='3'):
#     print('Please provide environment to connect to: ')
#     print('1. CT1 (1)\n2. WST (2)\n3. CT2 (3)')
#     environment_is=input()
# con = getConnection()
#
# # New Address Intake
# print("Please provide address to configure: ")
# new_address_postcode = input("Post Code: ")
# new_address_housenumber = input("House Number: ")
# new_address_housenumberext = input("House Number Ext: ")
# print(
#     "Values received: " + new_address_postcode + ", " + new_address_housenumber + ", " + new_address_housenumberext + ".")
#
# # Check if Address present in im_address_ext
# sql_checkAddressAvDb = f"select * from im_address_ext where addr_name1='{new_address_postcode}' and addr_name2='{new_address_housenumber}' and addr_name3{checkHouseNrExtIfNull()}"
# print(sql_checkAddressAvDb)  # Check query
# with con.cursor() as cur_validateAddress:
#     for countAvDb in cur_validateAddress.execute(sql_checkAddressAvDb):
#         new_address_count = cur_validateAddress.rowcount
#         print('Number of entries for Address in im_address_ext = '+str(new_address_count))
#     if new_address_count == 1:
#         address_exists = 'Y'
#         old_addressID = countAvDb[0]
#         print('Existing Address ID against below address: ' + str(old_addressID))
#     elif new_address_count > 1:
#         input('Multiple Address IDs found against the given address. Please check, correct the data.')
#         exit()
#     else:
#         old_addressID = input('Address does not exist in im_address_ext. Please provide Address_ID to replace: ')
#         getOldAddress()
#         # cur_validateAddress.execute('update im_address_ext set addr_name1=:2, addr_name2=:3, addr_name3=:4 where address_id=:1', (old_addressID,new_address_postcode,new_address_housenumber,new_address_housenumberext))
#         # con.commit()
#
# # Check if need to configure with GroupID or CarrierID
# groupid_or_carrierid='G'
#
# getGroupid_CarrierType()         # Take carrier_type, group_id
#
# # Configure im_cp_kpn for non-network
# update_im_cp_kpn()
#
# # Configure im_carrier_kpn
# print('Updating group_id in im_carrier_kpn')
# update_im_carrier_kpn()
#
# # Update im_bitrate_kpn     -- Get Bitrate_ID: select avdb_bit.nextval from dual
# print('Updating im_bitrate_kpn')
# if groupid_or_carrierid=='G':
#     update_im_bitrate_kpn_from_file()
# else:
#     input('Error! Something Wrong, check with KV')
#     exit()
#
#
# # Get Tab_ID
# if groupid_or_carrierid=='G':
#     print('Getting Tab_IDs for the GroupID')
#     sql_getTabIDs = f"select tab_id, tab_technologytype from im_tech_kpn where dp_id='{group_id}'"
#     with con.cursor() as cur_getTabIDs:
#         for fetched_tab_id in cur_getTabIDs.execute(sql_getTabIDs):
#             old_tabid_tech.append((fetched_tab_id[0], fetched_tab_id[1]))
#
# print(old_tabid_tech)
# print(next_bitrateid_tech)
#
# # Update im_carrier_kpn
# print('Updating IM_DP_2_TECH_KPN')
# with con.cursor() as cur_insertDP2TechKPN:
#     for i in range(0, len(next_bitrateid_tech)):
#         print('Value of i ='+str(i))
#         print('old_tabid_tech[i][0] : '+str(old_tabid_tech[i][0]))
#         print('getNewBitrateFromTech(old_tabid_tech[i][1]) : '+str(getNewBitrateFromTech(old_tabid_tech[i][1])))
#         sql_insertDP2TechKPN = f"insert into IM_DP_2_TECH_KPN(tab_id, group_id, bitrate_id ,carrier_id) VALUES ('{old_tabid_tech[i][0]}', {group_id}, '{getNewBitrateFromTech(old_tabid_tech[i][1])}','{carrier_id}')"
#         try:
#             print(sql_insertDP2TechKPN)
#             cur_insertDP2TechKPN.execute(sql_insertDP2TechKPN)
#             print('Inserted 1 Row')
#         except cx_Oracle.DatabaseError as e:
#             raise
#
# con.commit()
# con.close()
# input('Exiting the program')