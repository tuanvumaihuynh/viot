FROM golang:1.23.2-alpine AS builder

WORKDIR /app

COPY ./viot-background .

RUN go mod download

RUN go build -o main ./cmd/main.go


FROM alpine:3.20

COPY --from=builder /app/main /app/main

CMD ["/app/main"]
