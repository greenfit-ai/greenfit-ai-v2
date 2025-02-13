FROM condaforge/miniforge3:latest

WORKDIR /app/
COPY ./ /app/

RUN bash /app/conda_env.sh

EXPOSE 443
CMD ["bash", "/app/run.sh"]
