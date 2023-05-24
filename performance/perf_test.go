package perf

import (
	"context"
	"net/http"
	"testing"
)

func createPerfTestCase(model *http.Request) func(*testing.B) {
	client := http.DefaultClient
	return func(b *testing.B) {
		b.RunParallel(func(p *testing.PB) {
			for p.Next() {
				client.Do(model.Clone(context.TODO()))
			}
		})
	}

}

func BenchmarkSlipConcurrentOnInvalidModelParams(b *testing.B) {
	model, err := http.NewRequest("GET", "http://127.0.0.1:8000/test/args?arg1=dsf&arg2=dsd&arg3=4", nil)
	if err != nil {
		panic(err)
	}
	createPerfTestCase(model)(b)
}

func BenchmarkSlipConcurrentOnValidModelParams(b *testing.B) {
	model, err := http.NewRequest("GET", "http://127.0.0.1:8000/test/args?arg1=dsf&arg2=dsd&arg3=4", nil)
	model.Header.Add("Header-Str", "stringstring")
	if err != nil {
		panic(err)
	}
	createPerfTestCase(model)(b)
}

func BenchmarkSlipConcurrentValidRequestsToQueryString(b *testing.B) {
	model, err := http.NewRequest("GET", "http://127.0.0.1:8000/arg-str?s=dsf", nil)
	if err != nil {
		panic(err)
	}
	createPerfTestCase(model)(b)
}
