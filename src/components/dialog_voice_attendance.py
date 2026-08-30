import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_result import show_attendance_result
from datetime import datetime
import pandas as pd

@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.write("Record a student's audio saying 'I am present,' and the AI will recognize the student.")

    audio_data = None
    audio_data = st.audio_input("Record classroom audio")
    if st.button('Analyze audio', width='stretch', type='primary'):
        with st.spinner('Processing Audio data'):
            enrolled_res = supabase.table('subject_student').select('*, student(*)').eq('subject_id', selected_subject_id).execute()
            enrolled_student = enrolled_res.data
            if not enrolled_student:
                st.warning('No student enrolled in this course')
                return
            candidates_dict = {
                s['student']['student_id'] : s['student']['voice_embedding']
                for s in enrolled_student if s['student'].get('voice_embedding')
            }
            if not candidates_dict:
                st.error('No enrolled students have voice profile registerd.')
                return
            audio_bytes = audio_data.read()
            detected_score = process_bulk_audio(audio_bytes, candidates_dict)
            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            for node in enrolled_student:
                student = node['student']
                score = detected_score.get(student['student_id'], 0.0)
                is_present = bool(score>0)
                results.append({
                    "Name":student['name'],
                    "ID":student['student_id'],
                    "Source": score if is_present else '-',
                    "Status":"✅ Present" if is_present else "❌ Absent"

                })


                attendance_to_log.append({
                    'student_id':student['student_id'],
                    'subject_id':selected_subject_id,
                    'timestamp':current_timestamp,
                    'is_present':bool(is_present)
                })
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)
    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)


