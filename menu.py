import subprocess as sp
import sys

def install_jdk():
	cmd2='sudo rpm -ivh /home/jdk-8u171-linux-x64.rpm'
	dow2=sp.getstatusoutput(cmd2)

	if dow2[0]==0:
		print('JDK Installed\n')

	else:
		print('Error in Installation of JDK\n')
		print('Please Re-Run Python Script')
		sys.exit()

def install_hadoop():
	cmd2='sudo rpm -ivh /home/hadoop-1.2.1-1.x86_64.rpm --force'
	dow2=sp.getstatusoutput(cmd2)

	if dow2[0]==0:
		print('Hadoop Installed')

	else:
		print('Error in Installation of Hadoop\n')
		print('Please Re-Run Python Script')
		sys.exit()

def lvm_integration():
	print("""
		Press 1 : To list all the attached devices
		Press 2 : To Continue
	""")
	inp=int(input())

	if inp==1:
		output=sp.getstatusoutput("lsblk --noheadings --raw -o NAME,SIZE,TYPE,MOUNTPOINT | awk '$1~/[[:digit:]]/ && $2 == ""'  ")
		if output[0]==0:
			print("Name , Size , TYPE , MOUNTPOINT")
			print(output[1])
		else:
			print('No Device Attached, Please Attach The Devie And Re-Run The Python')
			sys.exit()

	else:
		pass

	#attaching device
	count=int(input("how many devices you have"))
	devlist=list()
	d=""

	for i in range(count):
		device=input('Enter the name of device{}'.format(i+1))
		devlist.append(device)
		d=d+' '+'/dev/'+device
		print('creating pv of device: {} '.format(device))
		cmd='sudo pvcreate /dev/{}'.format(device)            #creating PV
		out=sp.getstatusoutput(cmd)
		if out[0]==0:
			print('PV created')
		else:
			print('PV not Created')

	#Creating VG
	vname=input('Enter VG Name')
	cmd='sudo vgcreate {} {}'.format(vname,d)
	out=sp.getstatusoutput(cmd)

	if out[0]==0:
		print(out[1])

	else:
		print('unable to create VG')

	#Creating LV
	part=input('Enter Your partition or LV name')
	size=input('Enter Size of partition')
	cmd='sudo lvcreate {} --size {} --name -y'.format(vname,size,part)
	out=sp.getstatusoutput(cmd)

	if out[0]==0:
		print(out[1])

	else:
		print('unable to create LV')

	#formatting, craeting directory and mounting LV
	cmd='sudo mkfs.ext4 /dev/{0}/{1} ; mkdir /datanode ; mount /dev/{0}/{1} /datanode '.format(vname,part)
	out=sp.getstatusoutput(cmd)

	if out[0]==0:
		print('LV Mounted')
		print(out[1])

	else:
		print('Unable to mount LV to datanode ')	

def hdfsconf():
	cmd='wget -O /etc/hadoop/hdfs-site.xml https://slavesoftware.s3.ap-south-1.amazonaws.com/hdfs-site.xml'
	out=sp.getstatusoutput(cmd)

	if out[0]==0:
		print('hdfs-site.xml configured')
		print(out[1])

	else:
		print('Unable to configure hdfs-site.xml')

def coreconf():
	cmd='wget -O /etc/hadoop/core-site.xml https://slavesoftware.s3.ap-south-1.amazonaws.com/core-site.xml'
	out=sp.getstatusoutput(cmd)

	if out[0]==0:
		mip=input('Enter Master IP - ')
		with open('/etc/hadoop/core-site.xml') as f:
			text=f.read().replace('0.0.0.0',mip)

		with open('/core-site.xml', "w") as f:
			f.write(text)
		print('hdfs-site.xml configured')

	else:
		print('Unable to configure hdfs-site.xml')

def lvinde():
	print("""
			Press 1 - To increase size of LV attached to your hadoop client
			Press 2 - To decrease size of LV attached to your hadoop client
			Press 3 - To Exit 
			Press 4 - To Return on Main Menu
		""")
	ch=int(input("Enter Your Choice"))

	if ch==1:
		lvname=input("Enter Your LV Name ( /dev/vg/lv ) :- ")
		size=input("Enter Size to be increase")
		cmd='lvextend --resizefs --size +{} {}'.format(size,lvname)
		out=sp.getstatusoutput(cmd)
		if out[0]==0:
			print('LV Size Increased')
		else:
			print('Unable to increase LV Size')
		sys.exit()

	elif ch==2:
		lvname=input("Enter Your LV Name ( /dev/vg/lv ) :- ")
		size=input("Enter exact size you want to be in LV ")
		cmd='lvreduce --resizefs --size {} {} -y '.format(size,lvname)
		out=sp.getstatusoutput(cmd)
		if out[0]==0:
			print('LV Size Decreased')
		else:
			print('Unable to Decrease LV Size')
		sys.exit()

	elif ch==3:
		sys.exit()

	elif ch==4:
		main()

	else:
		print('Please Enter a Valid Choice')
		lvinde()


def dockfunc():
	print("""
		Press 1 - To Start Apache Webserver
		Press 2 - To Stop Apache Webserver
		Press 3 - Exit
		Press 4 - To Return on Main Menu
		""")
	ch=int(input("Enter your Choice : "))

	if ch==1:
		print('Setting Up Webserver on Docker')
		out=sp.getstatusoutput('sudo systemctl start docker && docker pull centos:latest')
		if out[0]==0:
			print('CentOS Downloaded')
		else:
			print('CentOS Already Exist')
		out=sp.getstatusoutput('sudo docker run -itd --name mohit_webserver centos')
		if out[0]==0:
			print('Docker Container Started')
			out1=sp.getstatusoutput('sudo docker exec mohit_webserver bash -c "yum update && yum install httpd -y && yum install wget -y && yum install net-tools -y " ')
			if out1[0]==0:
				print('Server is Starting')
				out2=sp.getstatusoutput('sudo docker exec mohit_webserver wget -O /var/www/html/task.html https://slavesoftware.s3.ap-south-1.amazonaws.com/task.html')
				if out2[0]==0:
					out3=sp.getstatusoutput('sudo docker exec mohit_webserver bash -c " /usr/sbin/httpd && ifconfig eth0 " ')
					print(out3[1])
				else:
					print('unable to download html file')
			else:
				print('Unable to install Pre-requisites')
		else:
			print('Unable to launch Docker Container')
	
	elif ch==2:
		out=sp.getstatusoutput('sudo docker stop mohit_webserver && docker rm mohit_webserver && docker rmi centos && systemctl stop docker')			
		if out[0]==0:
			print('Webserver Stopped')
		else:
			print('No webserver Exist')

	elif ch==3:
		sys.exit()

	elif ch==4:
		main()

	else:
		print('Enter A Valid Choice')
		dockfunc()

def pyconf():
	print('Launching Python on Docker \n')
	out=sp.getstatusoutput('sudo systemctl start docker && docker pull centos:latest')

	if out[0]==0:
		print('CentOS Downloaded')
	else:
		print('CentOS Already Exist')
	out=sp.getstatusoutput('sudo docker run -itd --name mohit_python centos')

	if out[0]==0:
		print('CentOS Installed')
		out2=sp.getstatusoutput('sudo docker exec mohit_python bash -c "yum update && yum install python3 -y && yum install wget " ')
		if out2[0]==0:
			print('downloading python script')
			out3=sp.getstatusoutput('sudo docker exec mohit_python wget -O /test.py https://slavesoftware.s3.ap-south-1.amazonaws.com/test.py')
			if out3[0]==0:
				print('File downloaded ')
				out4=sp.getstatusoutput('sudo docker exec mohit_python python3 /test.py')
				if out4[0]==0:
					print('running python script')
					print(out4[1])
				else:
					print('Unable to run pythn script')
			else:
				print('Unable to Download file ')
		else:
			print('Unable to install Pre-Requisites')
	else:
		print('Unable to run Docker Conatiner')
	print('\nNow Exiting System\n')
	sys.exit()



def Slavconf():
	#installing JDK
	o2='sudo yum list installed | grep jdk'
	ou2=pb.getstatusoutput(o2)

	if ou2[0]==0:
		print('jdk is installed')

	else:
		print('Downloading jdk\n')
		c=sp.getstatusoutput('sudo test -f /home/jdk-8u171-linux-x64.rpm')
		if c[0]==0:
			print('Installing JDK')
			install_jdk()
		else:
			cmd='sudo wget -O /home/jdk-8u171-linux-x64.rpm https://repo.huaweicloud.com/java/jdk/8u171-b11/jdk-8u171-linux-x64.rpm'
			dow=sp.getstatusoutput(cmd)
			if dow[0]==0:
				print('jdk downloaded , Now Installing it\n')
				install_jdk()
			else:
				print('Error in downloading jdk')

	#installing hadoop
	o1='sudo yum list installed | grep hadoop'
	ou1=sp.getstatusoutput(o1)

	if ou1[0]==0:
		print("Hadoop installed")

	else:
		print('Downloading Hadoop')
		c=sp.getstatusoutput('sudo test -f /home/hadoop-1.2.1-1.x86_64.rpm')
		if c[0]==0:
			print('Installing Hadoop')
			install_hadoop()
		else:
			cmd="wget -O /home/hadoop-1.2.1-1.x86_64.rpm https://archive.apache.org/dist/hadoop/core/hadoop-1.2.1/hadoop-1.2.1-1.x86_64.rpm"
			dow=sp.getstatusoutput(cmd)
			if dow[0]==0:
				print('Hadoop Downloaded, Now Installing')
				install_hadoop()
			else:
				print('Error in Downloading Hadoop')

	#Attaching LVM storage
	lvm_integration()

	#configuring hdfs and core-site file
	hdfsconf()
	coreconf()
	cmd='sudo systemctl stop firewalld && sudo systemctl disable firewalld && sudo hadoop-daemon.sh start datanode'
	out=sp.getstatusoutput(cmd)
	if out[0]==0:
		print('DataNode Started')
	else:
		print('Unable to configure hdfs-site.xml')
		sys.exit()


def hadfunc():
	print("""
		Press 1 - To configure Hadoop Slave with LVM functionality First Time
		Press 2 - To Start Hadoop Slave
		Press 3 - To Stop Hadoop Slave 
		Press 4 - To Exit
		Press 5 - To return on Main Menu
		""")
	ch=int(input('Enter Your Choice :- '))

	if ch==1:
		Slavconf()

	elif ch==2:
		cmd='sudo systemctl stop firewalld && sudo systemctl disable firewalld && sudo hadoop-daemon.sh start datanode'
		out=sp.getstatusoutput(cmd)
		if out[0]==0:
			print('DataNode Started')
		else:
			print('Unable to configure hdfs-site.xml')
			sys.exit()

	elif ch==3:
		cmd='sudo hadoop-daemon.sh stop datanode'
		out=sp.getstatusoutput(cmd)
		if out[0]==0:
			print('DataNode Stopped')
		else:
			print('Unable to configure hdfs-site.xml')
			sys.exit()
	
	elif ch==4:
		sys.exit()
	
	elif ch==5:
		main()

def main():
	print("""
		------------------------------------------------------------
		#                Python Automation Menu                    #
		------------------------------------------------------------
		#  Press 1 - To use Hadoop Slave Services with LVM         #
		#  Press 2 - To Increase or Decrease Size of Hadoop Slave  #
		#  Press 3 - To setup and HTTPD server on Docker           #
		#  Press 4 - To setup python on Docker                     #
		#  Press 5 - To Exit                                       #
		------------------------------------------------------------
		  """)
	choice=int(input("Enter your Choice -> "))

	if choice==1:
		hadfunc()

	elif choice==2:
		lvinde()

	elif choice==3:
		dockfunc()

	elif choice==4:
		pyconf()

	elif choice==5:
		sys.exit()	

	else:
		print('Please Enter A Valid Choice')
		main()

if __name__ == '__main__':
	main()
