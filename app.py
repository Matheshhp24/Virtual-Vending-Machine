from flask import Flask, render_template, Response, redirect, url_for, jsonify,session
import cv2
from cvzone.HandTrackingModule import HandDetector

app = Flask(__name__)

global redirect_to_sugar,redirect_to_count,redirect_to_result,page,counter,coffee_flag,tea_flag,milk_flag,sugar_flag,nosugar_flag,result_0,result_1,result_2
sugar_flag = False
nosugar_flag = False
page = 0
# result_0 = ""
# result_1 = ""
# result_2 = ""
counter = 0
redirect_to_sugar = False
redirect_to_count = False
redirect_to_result = False
coffee_flag = False
tea_flag = False
milk_flag = False
# Function to capture video frames
def generate_frames():
    global redirect_to_sugar,redirect_to_count,redirect_to_result,page,counter,coffee_flag,tea_flag,milk_flag,sugar_flag,nosugar_flag,result_0,result_1,result_2
    sugar_flag = False
    nosugar_flag = False
    redirect_to_sugar = False 
    redirect_to_count = False
    redirect_to_result = False
    coffee_flag = False
    tea_flag = False
    milk_flag = False
    flag = -1
    counter = 0
    selection = 0
    
    items = ["Coffee","Tea","Milk"]
    sugar_choice = ["Sugar","No Sugar"]
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        if hands:
            hand1 = hands[0]
            fingers = detector.fingersUp(hand1)
            print(fingers)
            if fingers == [0,1,0,0,0]:# index
                if flag != 1:
                    counter = 1
                flag = 1
                selection = 1
                
                coffee_flag = True
                tea_flag = False
                milk_flag = False   
                sugar_flag = True
                nosugar_flag = False
                    
            elif fingers == [0,1,1,0,0]: # index and middle
    
                coffee_flag = False
                tea_flag = True
                milk_flag = False 
                sugar_flag = False
                nosugar_flag = True
                
                if flag != 2:
                    counter = 1
                flag = 2
                selection = 2
            elif fingers == [0,1,1,1,0]:  # index, middle, ring
                
                coffee_flag = False
                tea_flag = False
                milk_flag = True
                
                if flag != 3:
                    counter = 1
                flag = 3  
                selection = 3
                
                sugar_flag=False
                nosugar_flag = False
            else:  # resetting
                counter = 0
                flag = -1
                selection = 0
                
                coffee_flag = False
                tea_flag = False
                milk_flag = False
                sugar_flag=False
                nosugar_flag = False
            if counter > 0:
                counter +=1
            print(counter)
            if page == 0:
                if counter == 40 and selection == 1 or counter == 40 and selection == 2 or counter == 40 and selection == 3:
                    print(items[selection-1])
                    result_0 = items[selection-1]
                    flag = -1
                    counter = 0
                    selection = 0
                    redirect_to_sugar = True
                    break
            elif page == 1:
                if counter == 40 and selection == 1 or counter == 40 and selection == 2:
                    print(sugar_choice[selection-1])
                    result_1 = sugar_choice[selection-1]
                    flag = -1
                    counter = 0
                    selection = 0
                    redirect_to_count = True
                    break
            elif page == 2:
                if counter == 40 and selection == 1 or counter == 40 and selection == 2 or counter == 40 and selection == 3:
                    result_2 = selection
                    page=0
                    flag = -1
                    counter = 0
                    selection = 0
                    redirect_to_result = True
                    break
        else:
            coffee_flag = False
            tea_flag = False
            milk_flag = False
            sugar_flag=False
            nosugar_flag = False
            
        # print(page)
        ret, frame = cv2.imencode('.jpg', img)
        data = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')


@app.route('/get_flags_status')
def get_flags_status():
    return jsonify({
        'coffee_flag': coffee_flag,
        'tea_flag': tea_flag,
        'milk_flag': milk_flag,
        'sugar_flag':sugar_flag,
        'nosugar_flag':nosugar_flag
    })
@app.route('/get_results')
def get_results():
    return jsonify({
        'result_0': result_0,
        'result_1':result_1,
        'result_2':result_2
    })
    
@app.route('/redirect_check')
def redirect_check():
    if redirect_to_sugar:
        redirect_to_sugar = False
        return redirect(url_for('sugar'))
    elif redirect_to_count:
        redirect_to_count = False
        return redirect(url_for('count'))
    elif redirect_to_result:
        redirect_to_result = False
        return redirect(url_for('result'))
    return "Not redirecting"

# API endpoint to get the value of redirect_to_sugar
@app.route('/get_redirect_status')
def get_redirect_status():
    global redirect_to_sugar, redirect_to_count
    return jsonify({'redirect_to_sugar': redirect_to_sugar, 'redirect_to_count': redirect_to_count,'redirect_to_result': redirect_to_result})

@app.route('/sugar')
def sugar():
    global page
    page = 1
    return render_template('sugar.html')

@app.route('/count')
def count():
    global page
    page = 2
    return render_template('count.html')

@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/')
def index():
    global page
    page = 0
    return render_template('index_cam.html',counter = counter)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
