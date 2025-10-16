import os
import json
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler

# [수정] analyzer와 visualizer 모듈 임포트
import analyzer
import visualizer

# --- 설정 부분 ---
JSON_FILE_DIRECTORY = "//N28/shared/uploads/report"
GENERATED_FILES_DIRECTORY = os.path.join(JSON_FILE_DIRECTORY, "generated")
CHART_FILES_DIRECTORY = os.path.join(GENERATED_FILES_DIRECTORY, "charts")
REPORT_FILES_DIRECTORY = os.path.join(GENERATED_FILES_DIRECTORY, "reports")
# --- 설정 부분 끝 ---

app = Flask(__name__)


def scheduled_job():
    """스케줄러에 의해 주기적으로 실행될 전체 작업"""
    print(f"\n{datetime.now()}: 스케줄링된 작업을 시작합니다.")

    today_str = datetime.now().strftime('%Y-%m-%d')
    json_file_path = os.path.join(JSON_FILE_DIRECTORY, f"report_{today_str}.json")
    report_file_path = os.path.join(REPORT_FILES_DIRECTORY, f"daily_report_{today_str}.md")

    # 데이터 파일(.json) 로드
    if not os.path.exists(json_file_path):
        error_msg = f"오류: 데이터 파일({json_file_path})을 찾을 수 없습니다."
        print(error_msg)
        save_report_to_file(error_msg, report_file_path)
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except Exception as e:
        error_msg = f"오류: 데이터 파일({json_file_path})을 읽는 중 오류 발생: {e}"
        print(error_msg)
        save_report_to_file(error_msg, report_file_path)
        return

    # visualizer 모듈을 사용하여 그래프 생성
    print("데이터 시각화 이미지 생성을 시작합니다...")
    pie_chart_path = os.path.join(CHART_FILES_DIRECTORY, f"resource_sales_pie_{today_str}.png")
    visualizer.create_resource_sales_pie_chart(analysis_data.get('salesByResourceType'), pie_chart_path)

    bar_chart_path = os.path.join(CHART_FILES_DIRECTORY, f"hourly_sales_bar_{today_str}.png")
    visualizer.create_hourly_sales_bar_chart(analysis_data.get('salesByHourOfDay'), bar_chart_path)

    line_chart_path = os.path.join(CHART_FILES_DIRECTORY, f"new_user_trend_{today_str}.png")
    visualizer.create_new_user_trend_line_chart(analysis_data.get('newUserTrend'), line_chart_path)

    donut_chart_path = os.path.join(CHART_FILES_DIRECTORY, f"rating_distribution_{today_str}.png")
    visualizer.create_rating_distribution_donut_chart(analysis_data.get('ratingDistribution'), donut_chart_path)
    print("데이터 시각화 이미지 생성 완료.")

    # analyzer 모듈을 사용하여 텍스트 레포트 생성
    print("AI 텍스트 레포트 생성을 시작합니다...")
    report_content = analyzer.create_daily_report(analysis_data)

    # 생성된 레포트를 파일(.md)로 저장
    save_report_to_file(report_content, report_file_path)
    print("AI 텍스트 레포트 파일 저장 완료.")


def save_report_to_file(content, file_path):
    """주어진 내용을 지정된 경로의 파일로 저장하는 유틸리티 함수."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"레포트 파일 저장 중 오류 발생: {e}")

# ===== 수동 분석을 처리하는 API 엔드포인트 =====
@app.route('/trigger-analysis', methods=['POST'])
def trigger_analysis_manually():
    try:
        print("수동 분석 요청을 수신했습니다. 작업을 시작합니다.")
        # 기존 스케줄링 함수를 직접 호출하여 재사용
        scheduled_job()
        return jsonify({"status": "success", "message": "AI 분석 및 그래프 생성이 시작되었습니다. 잠시 후 페이지를 새로고침 해주세요."})
    except Exception as e:
        print(f"수동 분석 중 오류 발생: {e}")
        return jsonify({"status": "error", "message": f"분석 중 오류 발생: {e}"}), 500

@app.route('/get-latest-report-with-charts', methods=['GET'])
def get_latest_report_with_charts():
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        report_file_path = os.path.join(REPORT_FILES_DIRECTORY, f"daily_report_{today_str}.md")

        report_content = "생성된 레포트 파일이 없습니다."
        if os.path.exists(report_file_path):
            with open(report_file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()

        base_url = "http://localhost:5000/charts"

        charts = {
            "resource_sales_pie": f"{base_url}/resource_sales_pie_{today_str}.png",
            "hourly_sales_bar": f"{base_url}/hourly_sales_bar_{today_str}.png",
            "new_user_trend": f"{base_url}/new_user_trend_{today_str}.png",
            "rating_distribution": f"{base_url}/rating_distribution_{today_str}.png"
        }

        return jsonify({
            "report": report_content,
            "charts": charts
        })
    except Exception as e:
        return jsonify({"error": f"레포트/차트 조회 중 오류 발생: {e}"}), 500

@app.route('/charts/<filename>')
def serve_chart(filename):
    """생성된 차트 이미지 파일을 서빙하는 엔드포인트."""
    return send_from_directory(CHART_FILES_DIRECTORY, filename)

# 루트 URL(http://127.0.0.1:5000/)에 접속했을 때 "Hello, World!"를 반환
@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    # 모든 디렉토리 미리 생성
    os.makedirs(CHART_FILES_DIRECTORY, exist_ok=True)
    os.makedirs(REPORT_FILES_DIRECTORY, exist_ok=True)

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(scheduled_job, 'cron', hour=2, minute=0)
    scheduler.start()

    # 서버 시작 시 한번 즉시 실행 (테스트용)
    print("서버 시작 시 초기 작업을 1회 실행합니다.")
    scheduled_job()

    print("Flask 서버를 시작합니다...")
    app.run(host='0.0.0.0', port=5000)