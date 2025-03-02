@app.route('/done')
def done():
    global video_stream, selected_class
    if video_stream:
        video_stream.stop()
        video_stream = None
    selected_class = None
    return redirect(url_for('index'))