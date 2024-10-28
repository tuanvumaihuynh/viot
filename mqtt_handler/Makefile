sqlc:
	sqlc generate

test:
	go test -v -cover -short ./...

server:
	go run cmd/main.go

.PHONY: sqlc test server
