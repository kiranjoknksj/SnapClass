import streamlit as st

def footer_home():
    logo_url = "https://imgs.search.brave.com/cGlC_Kg4r8_YKflxnrNdPJZEejlLGHqYAIQmFqpgskg/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9sb2dv/cy5mbGFtaW5ndGV4/dC5jb20vTmFtZS1M/b2dvcy9LaXJhbi1k/ZXNpZ24tY2hpbmEt/bmFtZS5wbmc"
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:white;"> Created with ❤️ by </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)






def footer_dashboard():
    logo_url = "https://imgs.search.brave.com/cGlC_Kg4r8_YKflxnrNdPJZEejlLGHqYAIQmFqpgskg/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9sb2dv/cy5mbGFtaW5ndGV4/dC5jb20vTmFtZS1M/b2dvcy9LaXJhbi1k/ZXNpZ24tY2hpbmEt/bmFtZS5wbmc"
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:black;"> Created with ❤️ by </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)


    







# def teacher_tab_take_attendance():
#     teacher_id = st.session_state.teacher_data['teacher_id']
#     st.header('Take AI Attendance')


#     if 'attendance_images' not in st.session_state:
#         st.session_state.attendance_images = []

#     subjects = get_teacher_subject(teacher_id)

#     if not subjects:
#         st.warning('You havent created any subjects yet! Please create one to begin!')
#         return
    
#     subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

#     col1, col2 = st.columns([3,1], vertical_alignment='bottom')

#     with col1:
#         selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

#     with col2:
#         if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
#             add_photos_dialog()

#     selected_subject_id = subject_options[selected_subject_label]

#     st.divider()
#     if st.session_state.attendance_images:
#         st.header('Added Photos')
#         gallery_cols = st.columns(4)

#         for idx, img in enumerate(st.session_state.attendance_images):
#             with gallery_cols[idx % 4]:
#                 st.image(img, width='stretch', caption=f"Photo {idx+1}")
#     has_photos = bool(st.session_state.attendance_images)
#     c1, c2, c3 = st.columns(3)
#     with c1:
#         st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos)
#         st.session_state.attendance_images = []
#         st.rerun()
#     with c2:
#         if st.button('Rub Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
#             with st.spinner('Deep scanning classroom photos...'):
#                 all_detected_ids = {}
#                 for idx, img in enumerate(st.session_state.attendance_images):
#                     img_np = np.array(img.convert('RGB'))
#                     detected, _, _ =  predict_attendence(img_np)

#                     if detected:
#                         for sid in all_detected_ids.keys():
#                             student_id = int(sid)

#                             all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")
#                 enrolled_res = supabase.table('subject_student').select('*, student('*')').eq('subject_id', selected_subject_id).execute()
#                 enrolled_student = enrolled_res.data
#                 if not enrolled_student:
#                     st.warning('No student enrolled in this course')
#                 else:
#                     results, attendance_to_log = [], []
#                     current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
#                     for node in enrolled_student:
#                         student = node['students']
#                         sources = all_detected_ids.sget(int(student['student_id']), [])
#                         is_present = len(sources) > 0
#                         results.append({
#                             "Name":student['name'],
#                             "ID":student['student_id'],
#                             "Source":", ".join(sources) if is_present else "-",
#                             "Status":"✅ Present" if is_present else "❌ Absent"

#                         })


#                         attendance_to_log.append({
#                             'student_id':student['student_id'],
#                             'subject_id':selected_subject_id,
#                             'timestamp':current_timestamp,
#                             'is_present':bool(is_present)
#                         })
#                 attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
#     with c3:
#         if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
#             voice_attendance_dialog()