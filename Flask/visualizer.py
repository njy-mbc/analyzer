# visualizer.py

import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --- 한글 폰트 설정 ---
# 폰트가 없는 경우를 대비한 예외 처리 포함
try:
    font_path = 'c:/Windows/Fonts/malgun.ttf'
    if os.path.exists(font_path):
        plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())
    else:
        # Mac OS의 경우
        font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        if os.path.exists(font_path):
            plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())
        else:
            print("경고: 지정된 한글 폰트 파일을 찾을 수 없습니다. (malgun.ttf, AppleGothic.ttf)")
    # 한글 사용 시 마이너스 부호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"폰트 설정 중 오류 발생: {e}")


# --- 한글 폰트 설정 끝 ---


def create_resource_sales_pie_chart(data, save_path):
    """리소스 타입별 매출 파이 차트를 생성하고 저장합니다."""
    if not data:
        print("  - (SKIP) 리소스 매출 데이터가 없어 파이 차트를 생성하지 않습니다.")
        return

    try:
        df = pd.DataFrame(data)
        plt.figure(figsize=(8, 6))

        # 매출액이 0인 카테고리는 '기타'로 묶거나 제외할 수 있음
        wedges, texts, autotexts = plt.pie(df['totalAmount'],
                                           labels=df['categoryName'],
                                           autopct='%1.1f%%',
                                           startangle=140,
                                           pctdistance=0.85,
                                           colors=['#dc3545', '#0d6efd', '#ffc107', '#198754', '#6f42c1'])

        # 도넛 차트 효과
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.title('오늘의 리소스 종류별 매출 비중', fontsize=16)
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"  - 리소스 매출 파이 차트 저장 완료: {save_path}")
    except Exception as e:
        print(f"  - 리소스 파이 차트 생성 오류: {e}")


def create_hourly_sales_bar_chart(data, save_path):
    """시간대별 매출 막대 그래프를 생성하고 저장합니다."""
    if not data:
        print("  - (SKIP) 시간대별 매출 데이터가 없어 막대 그래프를 생성하지 않습니다.")
        return

    try:
        df = pd.DataFrame(data).set_index('hour')
        df = df.reindex(range(24), fill_value=0)  # 없는 시간은 0으로 채움

        plt.figure(figsize=(12, 6))
        bars = plt.bar(df.index, df['totalAmount'], color='#0d6efd', width=0.6)

        plt.title('오늘의 시간대별 매출 현황', fontsize=16)
        plt.xlabel('시간 (0-23시)')
        plt.ylabel('매출액 (원)')
        plt.xticks(range(24), rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # 막대 위에 값 표시 (선택사항)
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{int(height / 1000)}k', ha='center',
                         va='bottom')

        plt.savefig(save_path)
        plt.close()
        print(f"  - 시간대별 매출 막대 그래프 저장 완료: {save_path}")
    except Exception as e:
        print(f"  - 시간대별 막대 그래프 생성 오류: {e}")


# ===== 가입자 추이 라인 차트 생성 =====
def create_new_user_trend_line_chart(data, save_path):
    """지난 30일간의 신규 가입자 추이 라인 차트를 생성하고 저장"""
    if not data:
        print("  - (SKIP) 신규 가입자 데이터가 없어 라인 차트를 생성하지 않습니다.")
        return

    try:
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])  # 날짜 문자열을 datetime 객체로 변환
        df = df.set_index('date')

        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['count'], marker='o', linestyle='-', color='#198754')

        plt.title('최근 30일 신규 가입자 추이', fontsize=16)
        plt.xlabel('날짜')
        plt.ylabel('가입자 수')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        plt.savefig(save_path)
        plt.close()
        print(f"  - 신규 가입자 추이 라인 차트 저장 완료: {save_path}")
    except Exception as e:
        print(f"  - 신규 가입자 라인 차트 생성 오류: {e}")


# ===== 리뷰 평점 분포 도넛 차트 생성 =====
def create_rating_distribution_donut_chart(data, save_path):
    """리뷰 평점 분포를 도넛 차트로 생성하고 저장합니다."""
    if not data:
        print("  - (SKIP) 리뷰 평점 데이터가 없어 도넛 차트를 생성하지 않습니다.")
        return

    try:
        df = pd.DataFrame(data).set_index('rating')
        # 1점~5점에 대한 데이터 보장 (없는 평점은 0으로 채움)
        df = df.reindex(range(1, 6), fill_value=0)

        labels = [f'{i}점' for i in df.index]
        sizes = df['count']

        plt.figure(figsize=(8, 6))
        wedges, texts, autotexts = plt.pie(sizes,
                                           labels=labels,
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           pctdistance=0.85,
                                           colors=['#dc3545', '#fd7e14', '#ffc107', '#198754', '#0d6efd'])
        # 도넛 모양 만들기
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.title('전체 리뷰 평점 분포', fontsize=16)
        plt.axis('equal')  # 원형을 유지
        plt.tight_layout()

        plt.savefig(save_path)
        plt.close()
        print(f"  - 리뷰 평점 분포 도넛 차트 저장 완료: {save_path}")
    except Exception as e:
        print(f"  - 리뷰 평점 도넛 차트 생성 오류: {e}")