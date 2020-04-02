[33mcommit 027e16cbe98a3bfe5311be5fa8b2b8a69275e5b6[m[33m ([m[1;36mHEAD -> [m[1;32mmaster[m[33m, [m[1;31morigin/master[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Author: Danil <SivtsovDT@gmail.com>
Date:   Thu Apr 2 19:25:55 2020 +0300

    change to working OPC-UA

[1mdiff --git a/sgk-project-backend/OPC-ua/client.py b/sgk-project-backend/OPC-ua/client.py[m
[1mindex 97e0c6d..c8f437c 100644[m
[1m--- a/sgk-project-backend/OPC-ua/client.py[m
[1m+++ b/sgk-project-backend/OPC-ua/client.py[m
[36m@@ -3,23 +3,21 @@[m [mimport time[m
 import pika[m
 from opcua.tools import embed[m
 [m
[31m-URL = 'opc.tcp://0.0.0.0:4840'[m
[32m+[m[32mURL = 'opc.tcp://server:4840/'[m
 PERIOD = 100[m
 [m
 params = {}[m
[31m-#лист с данными[m
 total = [][m
 channel = ''[m
 [m
 class SubHandler(object):[m
 [m
[31m-	def event_notification(self, event):[m
[31m-	    print("New event recived: ", event)[m
[31m-	#пробовал в этом методе брать имя параметра, как node.get_browse_name().name[m
[32m+[m[32m    #пробовал в этом методе брать имя параметра, как node.get_browse_name().name[m
 	#но таким образом этот метод вообще перестает работать, происходит timeout постоянно[m
 	#наверно при get_browse_name происходит обращение к серверу, а это дорого[m
 	#в итоге закинул имена параметров в словарь params - {nodeid, param_name}[m
 	def datachange_notification(self, node, val, data):[m
[32m+[m		[32mprint((params[node.nodeid.Identifier] , val))[m
 		total.append((params[node.nodeid.Identifier] , val))[m
 [m
 		#channel.basic_publish(exchange= '',[m
[36m@@ -28,7 +26,6 @@[m [mclass SubHandler(object):[m
 		#properties = pika.BasicProperties(delivery_mode=2))[m
 [m
 if __name__ == "__main__":[m
[31m-[m
 	client = Client(URL)[m
 [m
 	try:[m
[36m@@ -54,12 +51,16 @@[m [mif __name__ == "__main__":[m
 		#подписка на изменения среди данных параметров[m
 		msclt = SubHandler()[m
 		sub = client.create_subscription(PERIOD, msclt)[m
[31m-		handle = sub.subscribe_data_change(vars)[m
[32m+[m		[32mhandle_data = sub.subscribe_data_change(vars)[m
[32m+[m		[32mhandle_events = sub.subscribe_events()[m
[32m+[m
[32m+[m		[32mwhile(True):[m
[32m+[m			[32ma = 1[m
 [m
[31m-		#удобная замена while(True)[m
[32m+[m		[32m#embed - это терминал, он был в примерах библиотеки opcua вместо while(True)[m
 		#причем в терминале можно работать с локальными переменными в live режиме[m
 		embed()[m
[31m-		for h in handle:[m
[32m+[m		[32mfor h in handle_data:[m
 			sub.unsubscribe(h)[m
 		sub.delete()[m
 	finally:[m
[1mdiff --git a/sgk-project-backend/OPC-ua/clientDocker b/sgk-project-backend/OPC-ua/clientDocker[m
[1mindex c94ef2e..38a0cba 100644[m
[1m--- a/sgk-project-backend/OPC-ua/clientDocker[m
[1m+++ b/sgk-project-backend/OPC-ua/clientDocker[m
[36m@@ -1,6 +1,8 @@[m
 FROM python:3.6[m
 [m
 RUN pip install opcua pika IPython cryptography xlrd[m
[32m+[m
[32m+[m
 WORKDIR /code[m
 COPY client.py /code[m
 COPY wait-for-it.sh /code[m
[1mdiff --git a/sgk-project-backend/OPC-ua/docker-compose.yml b/sgk-project-backend/OPC-ua/docker-compose.yml[m
[1mindex 311bb06..87226f6 100644[m
[1m--- a/sgk-project-backend/OPC-ua/docker-compose.yml[m
[1m+++ b/sgk-project-backend/OPC-ua/docker-compose.yml[m
[36m@@ -1,10 +1,10 @@[m
[31m-version: '2.2'[m
[32m+[m[32mversion: '3'[m
 services:[m
[31m-  opcua:[m
[31m-    image: "python:3.6"[m
[31m-    ports: [m
[31m-     - "4840:4840"  [m
[31m-     - "5672:5672"[m
[32m+[m[32m  server:[m
[32m+[m[32m    build:[m[41m [m
[32m+[m[32m      context: .[m
[32m+[m[32m      dockerfile: serverDocker[m
[32m+[m[32m    restart: always[m
   client:[m
     build: [m
       context: .[m
[36m@@ -12,8 +12,6 @@[m [mservices:[m
     restart: always[m
     depends_on: [m
      - server[m
[31m-  server:[m
[31m-    build: [m
[31m-      context: .[m
[31m-      dockerfile: serverDocker[m
[31m-    restart: always[m
\ No newline at end of file[m
[32m+[m[32m    links:[m
[32m+[m[32m     - "server"[m[41m [m
[41m+  [m
[1mdiff --git a/sgk-project-backend/OPC-ua/server.py b/sgk-project-backend/OPC-ua/server.py[m
[1mindex 09e9d7a..cc2ab59 100644[m
[1m--- a/sgk-project-backend/OPC-ua/server.py[m
[1m+++ b/sgk-project-backend/OPC-ua/server.py[m
[36m@@ -5,7 +5,7 @@[m [mimport time[m
 import pandas as pd[m
 from IPython import embed[m
 [m
[31m-URL = 'opc.tcp://0.0.0.0:4840'[m
[32m+[m[32mURL = 'opc.tcp://0.0.0.0:4840/'[m
 FILE_NAME = 'ActualDataFeb2020.xlsx'[m
 TIMEOUT = 5[m
 [m
[36m@@ -16,7 +16,7 @@[m [mif __name__ == "__main__":[m
 	server.set_endpoint(URL)[m
 	addspace = server.register_namespace(name)[m
 	node = server.get_objects_node()[m
[31m-[m
[32m+[m	[32mprint("||||||||||||||")[m
 	#добавление объекта[m
 	Param = node.add_object(addspace, 'WATER')[m
 [m
[1mdiff --git a/sgk-project-backend/OPC-ua/serverDocker b/sgk-project-backend/OPC-ua/serverDocker[m
[1mindex 3405848..48e45dc 100644[m
[1m--- a/sgk-project-backend/OPC-ua/serverDocker[m
[1m+++ b/sgk-project-backend/OPC-ua/serverDocker[m
[36m@@ -4,6 +4,7 @@[m [mRUN pip install opcua IPython cryptography xlrd pandas[m
 WORKDIR /code[m
 COPY server.py /code[m
 COPY ActualDataFeb2020.xlsx /code[m
[32m+[m[32mCOPY wait-for-it.sh /code[m
 EXPOSE 4840[m
 [m
 CMD ["python", "/code/server.py"][m
\ No newline at end of file[m
