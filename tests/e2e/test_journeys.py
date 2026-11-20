"""Browser journeys from docs/SCREENS.md, using semantic locators only."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def login(page, role_label: str) -> None:
    page.get_by_role("button", name=re.compile(role_label)).click()
    expect(page.get_by_role("heading", name="Tổng quan")).to_be_visible()


def test_permission_boundary(page):
    login(page, "Ban lãnh đạo")
    expect(page.get_by_role("button", name=re.compile("Brent Dated"))).to_be_visible()

    page.get_by_role("combobox", name="Vai trò").select_option("internal")
    expect(page.get_by_text("Dữ liệu hạn chế đã được ẩn theo quyền của bạn.")).to_be_visible()
    expect(page.get_by_role("button", name=re.compile("Brent Dated"))).to_have_count(0)
    expect(page.get_by_role("link", name="Quản trị")).to_have_count(0)

    page.goto("/#admin")
    expect(page.get_by_text("Bạn không có quyền truy cập màn hình này.")).to_be_visible()

    page.get_by_role("link", name="Trợ lý AI").click()
    page.get_by_role("button", name="What is the dated Brent physical price?").click()
    expect(page.get_by_text(re.compile("not available in your scope"))).to_be_visible()


def test_morning_triage(page):
    login(page, "Ban lãnh đạo")
    page.get_by_role("button", name=re.compile("Brent I · internal")).click()
    expect(page.get_by_role("heading", name="Brent Crude Futures")).to_be_visible()
    expect(page.get_by_text("Δ vs prior observation")).to_be_visible()

    page.goto("/#overview")
    page.get_by_role("button", name="Hỏi nhanh").click()
    page.get_by_label("Hỏi trợ lý").fill("What is the gasoline crack spread?")
    page.get_by_role("button", name="Gửi").click()
    expect(page.get_by_text(re.compile("AI interpretation"))).to_be_visible()
    expect(page.get_by_text(re.compile("13.68"))).to_be_visible()


def test_news_review(page):
    login(page, "Phân tích thị trường")
    page.get_by_role("link", name="Tin tức thị trường").click()
    page.get_by_label("Tất cả chủ đề").select_option("OPEC+")
    expect(page.get_by_role("button", name=re.compile("OPEC\\+ signals patience"))).to_be_visible()

    page.get_by_role("button", name=re.compile("OPEC\\+ signals patience")).click()
    expect(page.get_by_role("heading", name=re.compile("OPEC\\+ signals patience"))).to_be_visible()
    expect(page.get_by_text("AI summary")).to_be_visible()
    expect(page.get_by_text("AI insight")).to_be_visible()

    page.get_by_role("button", name="Đánh dấu quan trọng").click()
    expect(page.get_by_text("Đã lưu")).to_be_visible()


def test_forecast_check(page):
    login(page, "Ban lãnh đạo")
    page.get_by_role("link", name="Dự báo").click()
    page.get_by_label("Tất cả công cụ").select_option("brent_futures")
    expect(page.get_by_role("cell", name="EIA (demo)").first).to_be_visible()

    page.get_by_role("button", name="Lịch sử phiên bản").first.click()
    expect(page.get_by_role("heading", name=re.compile("Lịch sử phiên bản"))).to_be_visible()
    expect(page.get_by_role("dialog").get_by_role("cell", name="v3")).to_be_visible()


def test_report_generation_and_export(page):
    login(page, "Phân tích thị trường")
    page.get_by_role("link", name="Báo cáo").click()
    page.get_by_role("button", name="Tạo báo cáo").click()
    expect(page.get_by_role("heading", name=re.compile("On-demand Market Analysis"))).to_be_visible()

    with page.expect_download() as download_info:
        page.get_by_role("button", name="Xuất PDF").click()
    download = download_info.value
    assert download.suggested_filename.endswith(".pdf")


def test_event_marker_is_keyboard_activatable(page):
    login(page, "Ban lãnh đạo")
    marker = page.get_by_role("button", name="Red Sea freight disruption widens")
    marker.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("dialog").get_by_role("heading", name="Red Sea freight disruption widens")).to_be_visible()
    expect(page.get_by_role("dialog").get_by_text("Platts (demo)")).to_be_visible()


def test_quick_input(page):
    login(page, "Phân tích thị trường")
    page.get_by_role("button", name="Quan sát").click()
    page.get_by_label("Instrument").select_option("wti_futures")
    page.get_by_label("Giá trị").fill("75.5")
    page.get_by_label("Thời điểm").fill("2026-11-14T08:00")
    page.get_by_role("button", name="Gửi").click()
    expect(page.get_by_text("Đã lưu")).to_be_visible()
