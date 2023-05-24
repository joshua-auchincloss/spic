goos: darwin
goarch: amd64
pkg: performance
cpu: Intel(R) Core(TM) i5-8259U CPU @ 2.30GHz
BenchmarkSlipConcurrentOnInvalidModelParams-8         	    1000	   2865589 ns/op
BenchmarkSlipConcurrentOnValidModelParams-8           	    1000	   2718713 ns/op
BenchmarkSlipConcurrentValidRequestsToQueryString-8   	    1000	   1953865 ns/op
PASS
ok  	performance	7.937s
