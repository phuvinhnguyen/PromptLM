# SCoT
Topological software agent

```mermaid
graph TD;
    testgen ---> Done
    analyse ---> coder ---> testgen
    problem ---> testgen ---> analyse

    Done[Done:
    No more problem in the list]

    problem[Query includes problem and repo]

    testgen[Test generation:
    Use tools to search for relevant existing unit tests in the repo given the problem
    Given problem, repo, and existing tests. Generate a code piece and run it to check if the repo has problem
    If all tests passed, delete the problem and test the next problem]


    analyse[Analyse:
    Summary error log, analyse and search for possible error in the project, return new problem and location of error code]

    coder[Coder:
    given a code piece that is likely to have error, patch it correctly]
```

Create and solve new problem:
- main problem (m) -> test -> failed  
[m]
- create mini problem 1 -> solve -> test -> failed  
[m, m1]
- create mini problem 2 -> solve -> test -> failed  
[m, m1, m2]
- create mini problem 3 -> solve -> test -> ok -> m2 -> ok -> m1 -> ok -> m -> failed  
[m]
- create mini problem 4 -> solve -> test -> ok -> m -> ok  
[]
- empty -> no more problem -> done  