FROM python:3
EXPOSE 7005
ENV FLASK_DEBUG=1
ENV PORT=7005
RUN pip install flask
RUN pip install cerberus
RUN pip install requests
