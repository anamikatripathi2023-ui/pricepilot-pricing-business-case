from streamlit.testing.v1 import AppTest


def test_dashboard_renders_and_recommends_99():
    app = AppTest.from_file("../app.py", default_timeout=180).run()
    assert not app.exception
    assert len(app.tabs) == 5
    assert app.metric[0].value == "Rs 99"


def test_price_override_updates_dashboard():
    app = AppTest.from_file("../app.py", default_timeout=180).run()
    app.sidebar.checkbox[0].check().run()
    app.sidebar.slider[-1].set_value(149).run()
    assert not app.exception
    assert app.metric[0].value == "Rs 149"
