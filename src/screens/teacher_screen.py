import streamlit as st
import time
from src.database.config import supabase
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exits, create_teacher, teacher_login, get_teacher_subject,  get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendence
from src.components.dialog_attendance_result import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
import numpy as np
from datetime import datetime
import pandas as pd

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == 'login':
        teacher_screen_login()
    elif st.session_state.teacher_login_type == 'register':
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}")
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()
    

    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendence'

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = 'primary' if st.session_state.current_teacher_tab == 'take_attendence' else 'tertiary'
        if st.button('Take Attendence', type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendence'
            st.rerun()

    with tab2:
        type2 = 'primary' if st.session_state.current_teacher_tab == 'manage_subject' else 'tertiary'
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subject'
            st.rerun()

    with tab3:
        type3 = 'primary' if st.session_state.current_teacher_tab == 'attendance_records' else 'tertiary'
        if st.button('Attendance Records', type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendence':
        teacher_tab_take_attendance()

    if st.session_state.current_teacher_tab == 'manage_subject':
        teacher_tab_manage_subject()

    if st.session_state.current_teacher_tab == 'attendance_records':
        teacher_tab_attendence_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subject(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()
    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f"Photo {idx+1}")
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()
    with c2:
        if st.button('Rub Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ =  predict_attendence(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")
                enrolled_res = supabase.table('subject_student').select('*, student(*)').eq('subject_id', selected_subject_id).execute()
                enrolled_student = enrolled_res.data
                if not enrolled_student:
                    st.warning('No student enrolled in this course')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                    for node in enrolled_student:
                        student = node['student']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0
                        results.append({
                            "Name":student['name'],
                            "ID":student['student_id'],
                            "Source":", ".join(sources) if is_present else "-",
                            "Status":"✅ Present" if is_present else "❌ Absent"

                        })


                        attendance_to_log.append({
                            'student_id':student['student_id'],
                            'subject_id':selected_subject_id,
                            'timestamp':current_timestamp,
                            'is_present':bool(is_present)
                        })
                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subject():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')
    with col2:
        if st.button('Create New Subject', width='content'):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subject(teacher_id)
    if subjects:
        for sub in subjects:
            total_students = sub.get('total_student', 0)
            total_classes = sub.get('total_classes', 0)

            stats = [
                ('👥', 'Students', total_students),
                ('🕰️', 'Classes', total_classes)
            ]

            def share_btn():  # default arg captures current sub, avoids late-binding bug
                if st.button(f"Share code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=':material/share:'):
                    share_subject_dialog(sub['name'], sub['subject_code'])  
                st.space()
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats,
                footer_callback=share_btn
                )
    else:
        st.info('No subject found. Create One Above')
def teacher_tab_attendence_records():
    st.header('Attendance Records')
    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)
    if not records:
        return
    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            'ts_group':ts.split('.')[0] if ts else None,
            'Time':datetime.fromisoformat(ts).strftime('%Y-%m-%d %I:%M %p') if ts else 'N/A',
            'Subject':r['subject']['name'],
            'Subject_code':r['subject']['subject_code'],
            'is_present':bool(r.get('is_present', False)),
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject_code', 'is_present'])
        .agg(
            Present_count = ('is_present', 'sum'),
            total_count = ('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Stats'] = (
        '✅' + summary['Present_count'].astype(str) + '/'
        + summary['total_count'].astype(str) + 'Students'
    )

    display_df = (summary.sort_values(by='ts_group', ascending=False)
                  [['Time', 'Subject', 'Subject_code', 'Attendance Stats']]
                  )
    st.dataframe(display_df,width='stretch', hide_index=True)

def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<h2 style='text-align:center;'>Login using password</h2>", unsafe_allow_html=True)
   
    st.divider()

    teacher_username = st.text_input("Enter username", placeholder='kiranchauhan')
    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()
    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut="control+enter", width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back", icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type='primary', icon=':material/passkey:', width='stretch', key='goto_register_btn'):
            st.session_state.teacher_login_type = 'register'
            st.rerun()

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_password, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_password:
        return False, "All fields are required!"
    if check_teacher_exits(teacher_username):
        return False, "Username already taken"
    if teacher_password != teacher_pass_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username, teacher_name, teacher_password)
        return True, "Successfully Created! Login now"
    except Exception as e:
        return False, "Unexpected error"


def teacher_screen_register():
    c11, c22 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c11:
        header_dashboard()
    with c22:
        if st.button("Go back to Home", type='secondary', key='registerbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Register your teacher profile')

    teacher_username = st.text_input("Enter username", placeholder="kiranchauhan")
    teacher_name = st.text_input("Enter name", placeholder="Kiran Chauhan")
    teacher_password = st.text_input("Enter password", type='password', placeholder="Enter password")
    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()
    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut="control+enter", width='stretch', key='register_submit_btn'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_password, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead', type='primary', icon=':material/passkey:', width='stretch', key='goto_login_btn'):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()