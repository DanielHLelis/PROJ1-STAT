simulation <- function(n, s, p0, tr, b) {
    #' @param n máquinas operantes
    #' @param s máquinas reservas
    #' @param p0 probabilidade de quebrar
    #' @param tr tempo de reparo
    #' @param b coeficiente de desgaste

    stopifnot(n > 0)
    stopifnot(s >= 0)
    stopifnot(p0 >= 0 & p0 <= 1)
    stopifnot(tr >= 0)
    stopifnot(b >= 0 & b <= 1)

    repair <- numeric() # máquinas em reparo (vetor vazio)
    tfunc <- rep(0, n) # tempo de funcionamento de cada máquina
    t <- 0 # tempo

    while (s >= 0) {

        ## para que a probabilidade permaneça entre 0 e 1
        ## escolhemos o mínimo entre 1 e p(k) := p0 + b * tfunc(k)
        prob <- pmin(1, p0 + b * tfunc)

        ## vetor lógico de <n> posições em que TRUE sinaliza uma quebra
        broken <- as.logical(rbinom(n, 1, prob))

        ## quantidade de máquinas que quebraram
        nbroken <- sum(broken)

        ## caso alguma máquina quebre
        if (nbroken > 0) {
            s <- s - nbroken # utiliza as máquinas reservas

            ## acrescenta as <nbroken> máquinas no vetor de reparo
            ## cada máquina é representada por um contador (tr)
            repair <- append(repair, rep(tr, nbroken))

            ## as máquinas que quebraram são imediatamente
            ## substituídas pelas reservas, o que implica em um
            ## tempo de funcionamento zerado para essas máquinas
            tfunc[broken] <- 0
        }

        ## caso haja máquinas em reparo
        if (length(repair) > 0) {

            repair <- repair - 1 # consome um tempo de reparo

            ## conta quantas máquinas o tempo de reparo finalizou
            ## (contador chegou em zero)
            fixed <- sum(repair == 0)

            if (fixed > 0) {
                ## coloca as máquinas reparadas
                ## de volta na reserva
                s <- s + fixed

                ## remove os contadores vazios
                repair <- setdiff(repair, 0)
            }
        }

        ## incrementa o tempo de funcionamento de cada máquina
        tfunc <- tfunc + 1
        ## incrementa o tempo total
        t <- t + 1
    }

    t # retorna t
}
