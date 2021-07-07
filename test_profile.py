import pstats
p=pstats.Stats("./result1.out")

# p.print_stats()0
# p.sort_stats("calls").print_stats()

p.sort_stats("cumulative").print_stats()