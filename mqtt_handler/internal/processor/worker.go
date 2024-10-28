package processor

import "context"

type Worker interface {
	// Start the worker
	Start(ctx context.Context)
	// Stop the worker
	Stop()
}
