# Use PostgreSQL image
FROM postgres:16

# Expose default port
EXPOSE 5432

# Set required env variables 
ENV POSTGRES_PASSWORD=root
ENV POSTGRES_USER=root
ENV POSTGRES_DB=testdb

# Copy initialization SQL scripts
COPY init/*.sql /docker-entrypoint-initdb.d/
