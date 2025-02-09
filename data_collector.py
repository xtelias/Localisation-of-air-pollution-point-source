import pyodbc
from settings import start_time, end_time, station_id
from icecream import ic

# from sqlalchemy import create_engine
#
# con = create_engine('mssql+pyodbc://DESKTOP-REAG93M/eco7.tattest', driver={ODBC Driver 17 for SQL Server}, echo=True)

# connectionString = ("Driver={SQL Server Native Client 11.0};""Server=DESKTOP-REAG93M\MSSQLSERVER01;""Database=eco7.tattest;"
#                     "Trusted_Connection=yes")
# connectionString = ("Driver={ODBC Driver 17 for SQL Server};""Server=DESKTOP-A17BP4U;""Database=eco7.tattest;"
#                     "Trusted_Connection=yes")
#
# # FOR LENOVO:
# # connectionString = ("Driver={ODBC Driver 17 for SQL Server};""Server=localhost\SQLEXPRESS01;""Database=eco7.tattest;"
# #                     "Trusted_Connection=yes")
# # SQL Server Native Client 11.0
# # ODBC Driver 18 for SQL Server
# connection = pyodbc.connect(connectionString, autocommit=True)
#
# dbCursor = connection.cursor()
#
# requestString = (f"""SELECT [eco7.tattest].[dbo].[ESamples].[Id]
#       ,[BeginDateTimeUtc]
#       ,[EndDateTimeUtc]
#       ,[PointId]
#       ,[EnvironmentId]
# 	  ,[eco7.tattest].[dbo].[ESamples].[Global_StationId]
# 	  ,[ValueDec]
# 	  ,[ChannelId]
# 	  ,[ComponentId]
# 	  ,[ShortName]
# 	  ,[FullName]
# 	  ,[Name]
#   FROM [eco7.tattest].[dbo].[ESamples]
#   JOIN [eco7.tattest].[dbo].[EPoints] ON [eco7.tattest].[dbo].[EPoints].[Global_StationId] = [eco7.tattest].[dbo].[ESamples].[Global_StationId]
#   JOIN [eco7.tattest].[dbo].[EResults] ON [eco7.tattest].[dbo].[EResults].[SampleId] = [eco7.tattest].[dbo].[ESamples].[Id]
#   JOIN [eco7.tattest].[dbo].[EChannels] ON [eco7.tattest].[dbo].[EChannels].[Id] = [ChannelId]
#   JOIN [eco7.tattest].[dbo].[EComponents] ON [eco7.tattest].[dbo].[EComponents].[Id] = [ComponentId]
#   WHERE [BeginDateTimeUtc]<='{end_time}' AND [BeginDateTimeUtc]>='{start_time}' AND [eco7.tattest].[dbo].[ESamples].[Global_StationId] = '{station_id}'
#   ORDER BY [eco7.tattest].[dbo].[ESamples].[Id]  ASC""")
#
# dbCursor.execute(requestString)
#
# global concentration1
# global concentration2
# global concentration3
# global concentration3
# global concentration5
#
# concentration1 = [] #DNS-1SS id234
# concentration2 = [] #GZU_100 id 250
# concentration3 = [] #PSP Aktash id246
# concentration4 = [] #DNS 650 id252
# concentration5 = [] #Kaleikino id100
#
# for row in dbCursor:
#     if row.ChannelId == 177:
#         concentration1.append(float(row.ValueDec))
#     if row.ChannelId == 194:
#         concentration2.append(float(row.ValueDec))
#     if row.ChannelId == 206:
#         concentration3.append(float(row.ValueDec))
#     if row.ChannelId == 219:
#         concentration4.append(float(row.ValueDec))
#     if row.ChannelId == 150:
#         concentration5.append(float(row.ValueDec))
#     print("Sampleid:" + str(row.Id) + ' ' + str(row.FullName) + ' ' + "ValueDec:" + str(row.ValueDec))
#
#
# ic(concentration1)
# ic(concentration2)
# ic(concentration3)
# ic(concentration4)
# ic(concentration5)


def weather_data_collect():

    # FOR DESKTOP:
    connectionString = (
        "Driver={ODBC Driver 17 for SQL Server};""Server=DESKTOP-A17BP4U;""Database=eco7.tattest;"
        "Trusted_Connection=yes")

    # FOR LENOVO:
    # connectionString = (
    #     "Driver={ODBC Driver 17 for SQL Server};""Server=localhost\SQLEXPRESS01;""Database=eco7.tattest;"
    #     "Trusted_Connection=yes")

    connection = pyodbc.connect(connectionString, autocommit=True)

    dbCursor = connection.cursor()

    requestString = (f"""SELECT [eco7.tattest].[dbo].[ESamples].[Id]
          ,[BeginDateTimeUtc]
          ,[EndDateTimeUtc] 
          ,[PointId]
          ,[EnvironmentId]
    	  ,[eco7.tattest].[dbo].[ESamples].[Global_StationId]
    	  ,[ValueDec]
    	  ,[ChannelId]
    	  ,[ComponentId]
    	  ,[ShortName]
    	  ,[FullName]
    	  ,[Name]
      FROM [eco7.tattest].[dbo].[ESamples]
      JOIN [eco7.tattest].[dbo].[EPoints] ON [eco7.tattest].[dbo].[EPoints].[Global_StationId] = [eco7.tattest].[dbo].[ESamples].[Global_StationId]
      JOIN [eco7.tattest].[dbo].[EResults] ON [eco7.tattest].[dbo].[EResults].[SampleId] = [eco7.tattest].[dbo].[ESamples].[Id]  
      JOIN [eco7.tattest].[dbo].[EChannels] ON [eco7.tattest].[dbo].[EChannels].[Id] = [ChannelId] 
      JOIN [eco7.tattest].[dbo].[EComponents] ON [eco7.tattest].[dbo].[EComponents].[Id] = [ComponentId] 
      WHERE [BeginDateTimeUtc]<='{end_time}' AND [BeginDateTimeUtc]>='{start_time}' AND [eco7.tattest].[dbo].[ESamples].[Global_StationId] = '{station_id}'
      ORDER BY [eco7.tattest].[dbo].[ESamples].[Id]  ASC""")

    dbCursor.execute(requestString)

    wind_dir = []
    wind_vel = []

    rows = dbCursor.fetchall()

    for row in rows:
        if row.ComponentId == 59:
            x = [float(row.ValueDec)]
            wind_dir.append(x)
        elif row.ComponentId == 58:
            x = [float(row.ValueDec)]
            wind_vel.append(x)
    # print(row.BeginDateTimeUtc, row.ComponentId, row.ValueDec)
    connection.commit()
    return wind_dir, wind_vel


def fetch_data_for_single_point(time, station_id):
    """
    Получает данные о ветре и концентрации для одной временной точки.
    """
    connectionString = (
        "Driver={ODBC Driver 17 for SQL Server};""Server=DESKTOP-A17BP4U;""Database=eco7.tattest;"
        "Trusted_Connection=yes"
    )
    connection = pyodbc.connect(connectionString, autocommit=True)
    dbCursor = connection.cursor()

    # change 248 to '{station_id}' if needed
    requestString = f"""
            SELECT[eco7.tattest].[dbo].[ESamples].[Id]
            , [BeginDateTimeUtc]
            , [EndDateTimeUtc]
            , [PointId]
            , [EnvironmentId]
            , [eco7.tattest].[dbo].[ESamples].[Global_StationId]
            , [ValueDec]
            , [ChannelId]
            , [ComponentId]
            , [ShortName]
            , [FullName]
            , [Name]
            FROM [eco7.tattest].[dbo].[ESamples]
            JOIN [eco7.tattest].[dbo].[EPoints]
            ON [eco7.tattest].[dbo].[EPoints].[Global_StationId] = [eco7.tattest].[dbo].[ESamples].[Global_StationId]
            JOIN [eco7.tattest].[dbo].[EResults]
            ON [eco7.tattest].[dbo].[EResults].[SampleId] = [eco7.tattest].[dbo].[ESamples].[Id]
            JOIN [eco7.tattest].[dbo].[EChannels]
            ON [eco7.tattest].[dbo].[EChannels].[Id] = [ChannelId]
            JOIN [eco7.tattest].[dbo].[EComponents]
            ON [eco7.tattest].[dbo].[EComponents].[Id] = [ComponentId]
            WHERE [BeginDateTimeUtc]='{start_time}' AND [eco7.tattest].[dbo].[EComponents].[Id] IN (46, 58, 59) 
            AND [eco7.tattest].[dbo].[EPoints].[Global_StationId] = 248
            """
    dbCursor.execute(requestString)

    observed_concentration = None
    wind_speed = None
    wind_direction = None

    for row in dbCursor.fetchall():
        if row.ComponentId == 46:
            observed_concentration = float(row.ValueDec)
        elif row.ComponentId == 58:
            wind_speed = float(row.ValueDec)
        elif row.ComponentId == 59:
            wind_direction = float(row.ValueDec)

    if observed_concentration is None or wind_speed is None or wind_direction is None:
        raise ValueError("Не удалось найти все данные для указанной временной точки.")

    connection.commit()
    return observed_concentration, wind_speed, wind_direction


wind_dir, wind_vel = weather_data_collect()
# ic(wind_dir)
# ic(wind_vel)
# ic(len(wind_dir))
# ic(len(wind_vel))
# connection.commit()
