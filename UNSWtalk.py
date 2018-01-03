#!/web/cs2041/bin/python3.6.3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os,re,math,shutil,time,codecs,subprocess
from flask import Flask, render_template, session, request,session,url_for
from flask_mail import Mail,Message


students_dir = "dataset-small"

app = Flask(__name__,static_folder='', static_url_path='')
app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'coollingjsd@gmail.com',
    MAIL_PASSWORD = '1234567890q'
    )
mail = Mail(app)

def send_email(to, subject, message):

    mutt = [
            'mutt',
            '-s',
            subject,
            '-e', 'set copy=no',
            '-e', 'set realname=UNSWtalk',
            '--', to
    ]

    subprocess.run(
            mutt,
            input = message.encode('utf8'),
            stderr = subprocess.PIPE,
            stdout = subprocess.PIPE,
    )

@app.route('/', methods=['GET','POST'])
def start():
    return render_template('login.html')

#login to UNSWtalk
@app.route('/zidlogin',methods=['GET','POST'])
def zidlogin():
    zid = request.form.get('zid', '')
    password = request.form.get('password', '')
    dirname=students_dir+'/'+zid
    if os.path.exists(dirname) and os.path.exists(dirname+'/student.txt'):
        student=read_student_details(dirname+'/student.txt')
        if student['password']==password:
            posts=[]
            dirpath=[]
            if 'friends' in student:
                dirpath=student['friends'].lstrip('(').rstrip(')').split(',')
            dirpath.append(zid)
            for i in range(len(dirpath)):
                dirpath[i]=students_dir+'/'+dirpath[i].strip()
            print(dirpath)
            for path in dirpath:
                for root, dirs, files in os.walk(path):
                    newstudent = read_student_details(path + '/student.txt')
                    poto=0
                    if os.path.exists(path+'/img.jpg'):
                        poto=path+'/img.jpg'
                    for file in files:
                        if re.match(r'^\d+.txt$', file):
                            post_detail=[0]*8
                            post_detail[7]=file.strip('.txt')
                            post=read_student_details(path+'/'+file)
                            if 'time' in post:
                                post_detail[0]=re.sub('T',' ',post['time'].strip('+0000'))
                            if 'message' in post:
                                post_detail[1]=post['message']
                            if 'from' in post:
                                post_detail[2]=post['from']
                            if 'full_name' in newstudent:
                                post_detail[3] = newstudent['full_name']
                            else:
                                post_detail[3]=newstudent['zid']
                            post_detail[6]=newstudent['zid']
                            post_detail[4] = path
                            post_detail[5]=poto
                            posts.append(post_detail)
            posts.sort(reverse=True)
            print(posts)
            pagenumber = 1
            if len(posts) >= pagenumber * 5:
                num = pagenumber * 5
            else:
                num = len(posts)
            return render_template('postwall.html',zid=zid, posts=posts, pagenumber=1, len=len(posts),totalpage=math.ceil(len(posts) / 5),num=num)
        else:
            return render_template('login.html', error='Wrong password')
    else:
        return render_template('login.html',error='Unknown zid - are you enrolled in UNSWtalk?')

@app.route('/home', methods=['GET', 'POST'])
def home():
    zid = request.args.get('zid', '')
    dirname = students_dir + '/' + zid
    student = read_student_details(dirname + '/student.txt')
    posts = []
    dirpath = []
    if 'friends' in student:
        dirpath = student['friends'].lstrip('(').rstrip(')').split(',')
    dirpath.append(zid)
    for i in range(len(dirpath)):
        dirpath[i] = students_dir + '/' + dirpath[i].strip()
    print(dirpath)
    for path in dirpath:
        for root, dirs, files in os.walk(path):
            newstudent = read_student_details(path + '/student.txt')
            poto = 0
            if os.path.exists(path + '/img.jpg'):
                poto = path + '/img.jpg'
            for file in files:
                if re.match(r'^\d+.txt$', file):
                    post_detail = [0] * 8
                    post_detail[7] = file.strip('.txt')
                    post = read_student_details(path + '/' + file)
                    if 'time' in post:
                        post_detail[0] = re.sub('T', ' ', post['time'].strip('+0000'))
                    if 'message' in post:
                        post_detail[1] = post['message']
                    if 'from' in post:
                        post_detail[2] = post['from']
                    if 'full_name' in newstudent:
                        post_detail[3] = newstudent['full_name']
                    else:
                        post_detail[3] = newstudent['zid']
                    post_detail[6] = newstudent['zid']
                    post_detail[4] = path
                    post_detail[5] = poto
                    posts.append(post_detail)
    posts.sort(reverse=True)
    pagenumber = 1
    if len(posts) >= pagenumber * 5:
        num = pagenumber * 5
    else:
        num = len(posts)
    return render_template('postwall.html', zid=zid, posts=posts, pagenumber=1, len=len(posts),
                           totalpage=math.ceil(len(posts) / 5), num=num)

#register a new account
@app.route('/zidregister',methods=['GET','POST'])
def zidregister():
    full_name = request.form.get('register_full_name', '')
    zid = request.form.get('register_zid', '')
    password = request.form.get('register_password', '')
    email = request.form.get('register_email', '')
    dirname=students_dir+'/'+zid
    if not re.match(r'^z\d{7}$',zid) or not zid:
        return render_template('login.html', error2='Invalid zid')
    elif os.path.exists(dirname):
        return render_template('login.html', error2='Account exists')
    elif not password :
        return render_template('login.html', error2='Enter password')
    elif not full_name:
        return render_template('login.html', error2='Enter full name')
    elif not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",email):
        return render_template('login.html', error2='Enter valid mail')
    else:
        msg=Message(
            subject='UNSWtalk account activation',
            sender='coollingjsd@gmail.com',
            recipients=[email]
        )
        msg.html = "<h3>Welcome to UNSWtalk! Click to active your account:<a href='"+url_for(endpoint='newaccountactivate',_external=True)+"?zid="+zid+"'>active account</a></h3>"
        mail.send(msg)
        os.mkdir(students_dir + '/'+zid)
        f = open(students_dir + '/'+zid+'/tem.txt', 'w')
        f.write("zid: " + zid+"\n")
        f.write('password: ' + password+"\n")
        f.write('full_name: ' + full_name+"\n")
        f.write('email: ' + email+"\n")
        f.close()
        return render_template('login.html', error2='Waiting for activation of account... ')

#receive mail to activate new account
@app.route('/newaccountactivate',methods=['GET','POST'])
def newaccountactivate():
    zid = request.args.get('zid', '')
    if os.path.exists(students_dir+'/'+zid+'/tem.txt'):
        os.rename(students_dir + '/' + zid + '/tem.txt', students_dir + '/' + zid + '/student.txt')
    return render_template('login.html', error='Your account has been activated ')


@app.route('/newpost',methods=['GET','POST'])
def newpost():
    zid = request.form.get('zid', '')
    newtext = request.form.get('newtext', '')
    numpost=[]
    for root, dirs, files in os.walk(students_dir+'/'+zid):
        for file in files:
            if re.match(r'^\d+.txt$', file):
                numpost.append(int(file.strip('.txt')))
    if numpost:
        maxnum = max(numpost) + 1
    else:
        maxnum=0
    f = open(students_dir + '/' + zid + '/'+str(maxnum)+'.txt', 'w')
    f.write('message: '+newtext+'\n')
    f.write('from: '+zid+'\n')
    f.write('time: '+time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.localtime())+'\n')
    f.close()
    dirname = students_dir + '/' + zid
    student = read_student_details(dirname + '/student.txt')
    posts = []
    dirpath = []
    if 'friends' in student:
        dirpath = student['friends'].lstrip('(').rstrip(')').split(',')
    dirpath.append(zid)
    for i in range(len(dirpath)):
        dirpath[i] = students_dir + '/' + dirpath[i].strip()
    print(dirpath)
    for path in dirpath:
        for root, dirs, files in os.walk(path):
            newstudent = read_student_details(path + '/student.txt')
            poto = 0
            if os.path.exists(path + '/img.jpg'):
                poto = path + '/img.jpg'
            for file in files:
                if re.match(r'^\d+.txt$', file):
                    post_detail = [0] * 8
                    post_detail[7] = file.strip('.txt')
                    post = read_student_details(path + '/' + file)
                    if 'time' in post:
                        post_detail[0] = re.sub('T', ' ', post['time'].strip('+0000'))
                    if 'message' in post:
                        post_detail[1] = post['message']
                    if 'from' in post:
                        post_detail[2] = post['from']
                    if 'full_name' in newstudent:
                        post_detail[3] = newstudent['full_name']
                    else:
                        post_detail[3] = newstudent['zid']
                    post_detail[6] = newstudent['zid']
                    post_detail[4] = path
                    post_detail[5] = poto
                    posts.append(post_detail)
    posts.sort(reverse=True)
    pagenumber = 1
    if len(posts) >= pagenumber * 5:
        num = pagenumber * 5
    else:
        num = len(posts)
    return render_template('postwall.html', zid=zid, posts=posts, pagenumber=1, len=len(posts),
                           totalpage=math.ceil(len(posts) / 5), num=num)



@app.route('/search',methods=['GET','POST'])
def search():
    zid = request.args.get('zid', '')
    return render_template('search.html',zid=zid)

#search students and posts
@app.route('/searchresult',methods=['GET','POST'])
def searchresult():
    zid = request.form.get('zid', '')
    action = request.form.get('action', '')
    text = request.form.get('text', '')
    results=[]
    if action=='searchfriends':
        for root, dirs, files in os.walk(students_dir):
            for dir in dirs:
                if dir != zid:
                    student=read_student_details(students_dir+'/'+dir+'/student.txt')
                    if 'full_name' in student:
                        if re.search(text,student['full_name'],re.I):
                            result=[0]*3
                            result[2] = student['zid']
                            result[0] = student['full_name']
                            if os.path.exists(students_dir+'/'+dir+'/img.jpg'):
                                result[1]=students_dir+'/'+dir+'/img.jpg'
                            results.append(result)
        pagenumber = 1
        if len(results) >= pagenumber * 5:
            num = pagenumber * 5
        else:
            num = len(results)
        print(len(results),'geshushushsuhsu')
        print(num,'llllllllllllll')
        results.sort()
        return render_template('searchstudentresults.html',zid=zid,results=results,pagenumber=1,len=len(results),totalpage=math.ceil(len(results)/5),num=num)
    else:
        posts=[]
        for root, dirs, files in os.walk(students_dir):
            for dir in dirs:
                newstudent = read_student_details(students_dir + '/' + dir + '/student.txt')
                poto = 0
                if os.path.exists(students_dir + '/' + dir + '/img.jpg'):
                    poto = students_dir + '/' + dir + '/img.jpg'
                for root, dirs, files in os.walk(students_dir+'/'+dir):
                    for file in files:
                        if re.match(r'^\d+.txt$', file):
                            print(students_dir+'/'+dir+'/'+file,'zhegewenjianyouwenti')
                            post=read_student_details(students_dir+'/'+dir+'/'+file)
                            post_detail = [0] * 8
                            post_detail[7] = file.strip('.txt')
                            if 'message' in post:
                                if re.search(text, post['message'],re.I):
                                    if 'time' in post:
                                        post_detail[0] = post['time']
                                    post_detail[1] = post['message']
                                    if 'from' in post:
                                        post_detail[2] = post['from']
                                    if 'full_name' in newstudent:
                                        post_detail[3] = newstudent['full_name']
                                    else:
                                        post_detail[3] = newstudent['zid']
                                    post_detail[6] = newstudent['zid']
                                    post_detail[4] = students_dir + '/' + dir
                                    post_detail[5] = poto
                                    posts.append(post_detail)
        posts.sort(reverse=True)
        pagenumber=1
        if len(posts) >= pagenumber*5:
            num=pagenumber*5
        else:
            num=len(posts)
        print(posts,'mknibciavcyfyvcysuvdyuctct')
        return render_template('searchpostresults.html', zid=zid, posts=posts, pagenumber=1, len=len(posts),totalpage=math.ceil(len(posts) / 5),num=num)

#next page and previous page
@app.route('/page', methods=['GET', 'POST'])
def page():
    zid = request.args.get('zid', '')
    type = request.args.get('type', '')
    if type=='postpage':
        posts =  eval('('+request.args.get('posts', '')+')')
        pagenumber = eval('('+request.args.get('pagenumber', '')+')')
        len = eval('('+request.args.get('len', '')+')')
        totalpage = eval('('+request.args.get('totalpage', '')+')')
        ac = request.args.get('ac', '')
        if ac=='add':
            pagenumber+=1
        else:
            pagenumber-=1
        if len >= pagenumber*5:
            num=pagenumber*5
        else:
            num=len
        return render_template('searchpostresults.html', zid=zid, posts=posts, pagenumber=pagenumber, len=len,totalpage=totalpage,num=num)
    if type=='studentpage':
        results = eval('(' + request.args.get('results', '') + ')')
        pagenumber = eval('(' + request.args.get('pagenumber', '') + ')')
        len = eval('(' + request.args.get('len', '') + ')')
        totalpage = eval('(' + request.args.get('totalpage', '') + ')')
        ac = request.args.get('ac', '')
        if ac == 'add':
            pagenumber += 1
        else:
            pagenumber -= 1
        if len >= pagenumber * 5:
            num = pagenumber * 5
        else:
            num = len
        return render_template('searchstudentresults.html', zid=zid, results=results, pagenumber=pagenumber, len=len,
                               totalpage=totalpage,num=num)
    if type=='homepage':
        posts = eval('(' + request.args.get('posts', '') + ')')
        pagenumber = eval('(' + request.args.get('pagenumber', '') + ')')
        len = eval('(' + request.args.get('len', '') + ')')
        totalpage = eval('(' + request.args.get('totalpage', '') + ')')
        ac = request.args.get('ac', '')
        if ac == 'add':
            pagenumber += 1
        else:
            pagenumber -= 1
        if len >= pagenumber * 5:
            num = pagenumber * 5
        else:
            num = len
        return render_template('postwall.html', zid=zid, posts=posts, pagenumber=pagenumber, len=len,
                               totalpage=totalpage, num=num)

#show all friends
@app.route('/friendlist',methods=['GET','POST'])
def friendlist():
    zid = request.args.get('zid', '')
    dirpath = []
    student=read_student_details(students_dir+'/'+zid+'/student.txt')
    if 'friends' in student:
        dirpath = student['friends'].lstrip('(').rstrip(')').split(',')
    for i in range(len(dirpath)):
        dirpath[i] = students_dir + '/' + dirpath[i].strip()
    friends=[]
    print(dirpath,'llllll')
    for path in dirpath:
        print(path,'gggg')
        friend=[0]*3
        print(path+'/student.txt','lujin')
        frienddetail=read_student_details(path+'/student.txt')
        print(frienddetail,'biaoge')
        if "full_name" in frienddetail:
            friend[0]=frienddetail['full_name']
        else:
            friend[0]=frienddetail['zid']
        if os.path.exists(path+'/img.jpg'):
            friend[1]=path+'/img.jpg'
        friend[2]=frienddetail['zid']
        friends.append(friend)
    print(friends,'zuihouuuu')
    return render_template('friendstable.html',zid=zid,friends=friends,dirpath=dirpath)

#show friends datail
@app.route('/friend_page', methods=['GET','POST'])
def friend_page():
    zid = request.args.get('zid', '')
    friendzid = request.args.get('friendzid', '')
    frienddetail=read_student_details(students_dir+'/'+friendzid+'/student.txt')
    friendphoto=0
    if os.path.exists(students_dir+'/'+friendzid+'/img.jpg'):
        friendphoto=students_dir+'/'+friendzid+'/img.jpg'
    return render_template('friendpage.html',frienddetail=frienddetail,zid=zid,friendphoto=friendphoto)


#delete friends
@app.route('/deletefriend', methods=['GET','POST'])
def deletefriend():
    friendzid = request.form.get('friend', '')
    zid = request.form.get('zid', '')
    student=read_student_details(students_dir+'/'+zid+'/student.txt')
    names=[]
    if 'friends' in student:
        names = student['friends'].lstrip('(').rstrip(')').split(',')
        for i in range(len(names)):
            names[i]=names[i].strip()
        names.remove(friendzid)
        student['friends']='('+','.join(names)+')'
        if not names:
            del student['friends']
        write_student_detail(students_dir+'/'+zid+'/student.txt',student)
    fri = read_student_details(students_dir + '/' + friendzid + '/student.txt')
    names = []
    if 'friends' in fri:
        names = fri['friends'].lstrip('(').rstrip(')').split(',')
        for i in range(len(names)):
            names[i] = names[i].strip()
        names.remove(zid)
        fri['friends'] = '(' + ','.join(names) + ')'
        if not names:
            del fri['friends']
        write_student_detail(students_dir + '/' + friendzid + '/student.txt', fri)
    dirpath = []
    if 'friends' in student:
        dirpath = student['friends'].lstrip('(').rstrip(')').split(',')
    for i in range(len(dirpath)):
        dirpath[i] = students_dir + '/' + dirpath[i].strip()
    friends = []
    print(dirpath, 'llllll')
    for path in dirpath:
        print(path, 'gggg')
        friend = [0] * 3
        print(path + '/student.txt', 'lujin')
        frienddetail = read_student_details(path + '/student.txt')
        print(frienddetail, 'biaoge')
        if "full_name" in frienddetail:
            friend[0] = frienddetail['full_name']
        else:
            friend[0] = frienddetail['zid']
        if os.path.exists(path + '/img.jpg'):
            friend[1] = path + '/img.jpg'
        friend[2] = frienddetail['zid']
        friends.append(friend)
    print(friends, 'zuihouuuu')
    return render_template('friendstable.html', zid=zid, friends=friends, dirpath=dirpath)

#add a new friend
@app.route('/addfriend', methods=['GET','POST'])
def addfriend():
    friendzid = request.form.get('friend', '')
    zid = request.form.get('zid', '')
    student = read_student_details(students_dir + '/' + zid + '/student.txt')
    if 'friends' in student:
        names = student['friends'].lstrip('(').rstrip(')').split(',')
        for i in range(len(names)):
            names[i]=names[i].strip()
            if names[i]==friendzid:
                return render_template('search.html',error='You are already friends!',zid=zid)
    friend=read_student_details(students_dir + '/' + friendzid + '/student.txt')
    email=friend['email']
    msg = Message(
        subject='UNSWtalk friend request',
        sender='coollingjsd@gmail.com',
        recipients=[email]
    )
    msg.html = "<h3>Welcome to UNSWtalk! There is a new friend request from "+zid+":<a href='http://127.0.0.1:5000/addfriendactive?zid=" + zid + "&friend="+friendzid+"'>add friend</a></h3>"
    mail.send(msg)
    return render_template('search.html',error='Waiting student to comfirm friend request...',zid=zid)

#confirm to add a new friend
@app.route('/addfriendactive', methods=['GET','POST'])
def addfriendactive():
    friendzid = request.args.get('friend', '')
    zid = request.args.get('zid', '')
    student = read_student_details(students_dir + '/' + zid + '/student.txt')
    if 'friends' in student:
        names = student['friends'].lstrip('(').rstrip(')').split(',')
        for i in range(len(names)):
            names[i] = names[i].strip()
        if friendzid not in names:
            names.append(friendzid)
        line='('+','.join(names)+')'
    else:
        line = '(' + friendzid + ')'
    student['friends']=line
    write_student_detail(students_dir + '/' + zid + '/student.txt',student)
    fri = read_student_details(students_dir + '/' + friendzid + '/student.txt')
    if 'friends' in fri:
        names = fri['friends'].lstrip('(').rstrip(')').split(',')
        for i in range(len(names)):
            names[i] = names[i].strip()
        if zid not in names:
            names.append(zid)
        line = '(' + ','.join(names) + ')'
    else:
        line = '(' + zid + ')'
    fri['friends'] = line
    write_student_detail(students_dir + '/' + friendzid + '/student.txt', fri)
    return render_template('jj.html',error='You are friends now!')

@app.route('/selfprofile', methods=['GET','POST'])
def selfprofile():
    zid = request.args.get('zid', '')
    selfdetail=read_student_details(students_dir+'/'+zid+'/student.txt')
    friendphoto = 0
    if os.path.exists(students_dir+'/'+zid+'/img.jpg'):
        friendphoto=students_dir+'/'+zid+'/img.jpg'
    return render_template('selfdetail.html',zid=zid,selfdetail=selfdetail,selfphoto=friendphoto)


# edit profile
@app.route('/editprofile', methods=['GET','POST'])
def editprofile():
    zid = request.form.get('zid', '')
    full_name = request.form.get('full_name', '')
    program = request.form.get('program', '')
    birthday = request.form.get('birthday', '')
    details = request.form.get('details', '')
    student=read_student_details(students_dir+'/'+zid+'/student.txt')
    if full_name:
        student['full_name']=full_name
    if program:
        student['program'] = program
    if birthday:
        student['birthday'] = birthday
    if details:
        student['details'] = details
    write_student_detail(students_dir+'/'+zid+'/student.txt',student)
    friendphoto = 0
    if os.path.exists(students_dir+'/'+zid+'/img.jpg'):
        friendphoto=students_dir+'/'+zid+'/img.jpg'
    return render_template('selfdetail.html',zid=zid,selfdetail=student,selfphoto=friendphoto,error='Change saved')

@app.route('/password', methods=['GET','POST'])
def password():
    return render_template('changepassword.html')

#change password
@app.route('/changepassword', methods=['GET','POST'])
def changepassword():
    zid = request.form.get('zid', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    if not re.match(r'^z\d{7}$',zid) or not zid:
        return render_template('changepassword.html', error='Invalid zid')
    elif not os.path.exists(students_dir+'/'+zid):
        return render_template('changepassword.html', error='Account does not exist')
    elif not password :
        return render_template('changepassword.html', error='Enter password')
    elif not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",email):
        return render_template('changepassword.html', error='Enter valid mail')
    else:
        msg=Message(
            subject='UNSWtalk change password',
            sender='coollingjsd@gmail.com',
            recipients=[email]
        )
        msg.html = "<h3>Welcome to UNSWtalk! Click to change your password:<a href='http://127.0.0.1:5000/changepasswordconfirm?zid="+zid+"'>confirm change</a></h3>"
        mail.send(msg)
        f = open(students_dir + '/'+zid+'/tempassword.txt', 'w')
        f.write('password: ' + password+"\n")
        f.close()
        return render_template('login.html')

@app.route('/changepasswordconfirm', methods=['GET','POST'])
def changepasswordconfirm():
    zid = request.args.get('zid', '')
    password=read_student_details(students_dir + '/'+zid+'/tempassword.txt')
    student=read_student_details(students_dir + '/'+zid+'/student.txt')
    student['password']=password['password']
    write_student_detail(students_dir + '/'+zid+'/student.txt',student)
    os.remove(students_dir + '/'+zid+'/tempassword.txt')
    return render_template('login.html',error='Your password change successfully!')

@app.route('/comments', methods=['GET','POST'])
def comments():
    zid = request.args.get('zid', '')
    path = request.args.get('path', '')
    number = request.args.get('number', '')
    mainpost = eval('(' + request.args.get('mainpost', '') + ')')
    posts=[]
    for root, dirs, files in os.walk(path):
        for file in files:
            jj=re.match(number+'-\d+.txt$', file)
            if jj:
                post_detail=[0]*8
                post=read_student_details(path+'/'+file)
                post_detail[7] = file.strip('.txt')
                if 'time' in post:
                    post_detail[0] = re.sub('T', ' ', post['time'].strip('+0000'))
                if 'message' in post:
                    post_detail[1] = post['message']
                if 'from' in post:
                    post_detail[2] = post['from']
                    d=read_student_details(students_dir+'/'+str(post_detail[2])+'/student.txt')
                    if 'full_name' in d:
                        post_detail[3] = d['full_name']
                    else:
                        post_detail[3] = d['zid']
                    if os.path.exists(students_dir+'/'+str(post_detail[2])+'/img.jpg'):
                        post_detail[5] = students_dir+'/'+str(post_detail[2])+'/img.jpg'
                    post_detail[6] = d['zid']
                post_detail[4] = path
                posts.append(post_detail)
    posts.sort(reverse=True)
    return render_template('comments.html',zid=zid,mainpost=mainpost,posts=posts)


@app.route('/newcomments', methods=['GET','POST'])
def newcomments():
    zid = request.form.get('zid', '')
    path = request.form.get('path', '')
    number = request.form.get('number', '')
    newtext = request.form.get('newtext', '')
    mainpost = eval('(' + request.form.get('mainpost', '') + ')')
    print(mainpost,'kkkkkkkkkkk')
    numpost = []
    for root, dirs, files in os.walk(path):
        for file in files:
            jj=re.match(number+'-(\d+).txt$', file)
            if jj:
                numpost.append(int(jj.group(1)))
    if numpost:
        maxnum = max(numpost) + 1
    else:
        maxnum=0
    f = open(path + '/' + number+'-'+str(maxnum) + '.txt', 'w')
    f.write('message: ' + newtext + '\n')
    f.write('from: ' + zid + '\n')
    f.write('time: ' + time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.localtime()) + '\n')
    f.close()
    posts = []
    for root, dirs, files in os.walk(path):
        for file in files:
            jj = re.match(number + '-\d+.txt$', file)
            if jj:
                post_detail = [0] * 8
                post = read_student_details(path + '/' + file)
                post_detail[7] = file.strip('.txt')
                if 'time' in post:
                    post_detail[0] = re.sub('T', ' ', post['time'].strip('+0000'))
                if 'message' in post:
                    post_detail[1] = post['message']
                if 'from' in post:
                    post_detail[2] = post['from']
                    d = read_student_details(students_dir + '/' + str(post_detail[2]) + '/student.txt')
                    if 'full_name' in d:
                        post_detail[3] = d['full_name']
                    else:
                        post_detail[3] = d['zid']
                    if os.path.exists(students_dir + '/' + str(post_detail[2]) + '/img.jpg'):
                        post_detail[5] = students_dir + '/' + str(post_detail[2]) + '/img.jpg'
                    post_detail[6] = d['zid']
                post_detail[4] = path
                posts.append(post_detail)
    posts.sort(reverse=True)
    return render_template('comments.html', zid=zid, mainpost=mainpost, posts=posts)




#delete account
@app.route('/account', methods=['GET','POST'])
def account():
    zid = request.args.get('zid', '')
    ac = request.args.get('ac', '')
    if ac=='delete':
        student=read_student_details(students_dir+'/'+zid+'/student.txt')
        if 'friends' in student:
            names = student['friends'].lstrip('(').rstrip(')').split(',')
            for i in range(len(names)):
                names[i] = names[i].strip()
                fri=read_student_details(students_dir+'/'+names[i]+'/student.txt')
                if 'friends' in fri:
                    name = fri['friends'].lstrip('(').rstrip(')').split(',')
                    for j in range(len(name)):
                        name[j] = name[j].strip()
                    name.remove(zid)
                    fri['friends'] = '(' + ','.join(name) + ')'
                    if not name:
                        del fri['friends']
                    write_student_detail(students_dir + '/' + names[i] + '/student.txt', fri)
        shutil.rmtree(students_dir+'/'+zid)
    return render_template('login.html')


def read_student_details(paths):
    students_details={}
    students=[]
    with open(paths) as f:
        for line in f:
            students.append(line.strip().replace('#','').split(': '))

    for i in range(len(students)):
        if len(students[i])>2:
            l=': '.join(students[i][1:])
            students[i][1]=l
            students[i]=students[i][:2]
    for (name,value) in students:
        students_details[name] = value.strip()
    return students_details

def write_student_detail(path,student):
    with open(path,'w') as f:
        for key in student:
            line=key+': '+student[key]+'\n'
            f.write(line)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
