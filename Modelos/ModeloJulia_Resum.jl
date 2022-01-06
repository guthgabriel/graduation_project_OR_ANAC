#import Pkg
#Pkg.add("XLSX")
#Pkg.add("DataFrames")
#Pkg.add("JuMP")
#Pkg.add("Gurobi")
#Pkg.add("CPLEX")
#Pkg.add("Cbc")

using XLSX, DataFrames, JuMP, CPLEX, Gurobi, Cbc

@time begin
    arquivo = XLSX.readxlsx("Instancia/InstanciaA1_resum.xlsx")

    DEM = arquivo["DADOS!A2:E51"] 
    PD = arquivo["DADOS!G2:H128"]
    ORIGENS = arquivo["DADOS!J2:J17"] 
    DESTINOS = arquivo["DADOS!K2:K31"] 
    ARCOS = arquivo["DADOS!M2:P474"] 
    ALOC = arquivo["DADOS!R2:T2553"]
    ALOC_ATIV = arquivo["DADOS!V2:Y3912"]

    struct ALOCADO # Variavel de decisão
        p::String # Pessoa
        o::String # Origem
        d::String # Destino
    end

    struct ALOCADO_ATIVIDADE # Variavel de decisão
        p::String # Pessoa
        o::String # Origem
        d::String # Destino
        m::Int64 # Missao
    end

    struct TRANSPORTE # 
        o::String # Origem
        d::String # Destino
    end

    ALOCADO_GERAL = [ALOCADO(ALOC[i,1], ALOC[i,2], ALOC[i,3]) for i in 1:size(ALOC,1)];

    ALOCADO_MISSAO = [ALOCADO_ATIVIDADE(ALOC_ATIV[i,1], ALOC_ATIV[i,2], ALOC_ATIV[i,3], parse(Int64,ALOC_ATIV[i,4])) for i in 1:size(ALOC_ATIV,1)];

    ARCO_TRANSPORTE = [TRANSPORTE(ARCOS[i,1], ARCOS[i,2]) for i in 1:size(ARCOS,1)];

    CUSTO_TRANSPORTE = Dict{TRANSPORTE, Float64}(TRANSPORTE(ARCOS[i,1], ARCOS[i,2]) => ARCOS[i,3] for i in 1:size(ARCOS,1));
    TEMPO_TRANSPORTE = Dict{TRANSPORTE, Float64}(TRANSPORTE(ARCOS[i,1], ARCOS[i,2]) => ARCOS[i,4] for i in 1:size(ARCOS,1));
    DISPONIBILIDADE = Dict{String, Float64}(PD[i,1] => PD[i,2] for i in 1:size(PD,1));

    TEMPO_MISSAO = Dict{Int, Float64}(DEM[i,1] => DEM[i,4] for i in 1:size(DEM,1));

    m = Model(Cbc.Optimizer);

    set_time_limit_sec(m, 600);

    @variable(m, X[ALOCADO_GERAL], binary=true);
    @variable(m, Y[ALOCADO_MISSAO], binary=true);

    @objective(m, Min, sum(2*X[i]*CUSTO_TRANSPORTE[TRANSPORTE(i.o,i.d)] for i in ALOCADO_GERAL));

    @constraint(m, [d in 1:size(DEM,1)], sum(Y[j] for j in ALOCADO_MISSAO if j.m == DEM[d,1]) == DEM[d,5]);

    @constraint(m, TEMPO_RESTRICAO[pp in PD[:,1]], sum(Y[j]*TEMPO_MISSAO[j.m] for j in ALOCADO_MISSAO if j.p == pp) + 
            sum(2 * X[i] * TEMPO_TRANSPORTE[TRANSPORTE(i.o,i.d)] for i in ALOCADO_GERAL if i.p == pp) <= DISPONIBILIDADE[pp]);

    @constraint(m, [j in ALOCADO_MISSAO], X[ALOCADO(j.p, j.o, j.d)] >= Y[j]);

    optimize!(m)
end

open("Instancia/Resultados/B/B1/B1_resum_jl_gurobi.txt" , "w") do f
    println(f, solution_summary(m))
    println(f, "RESULTADO INTEIRO = ", objective_value(m))
    println(f,"\t")
    println(f, "VARIABLES = ", num_variables(m))
    println(f,"\t")
    println(f, "CONSTRAINTS = ", num_constraints(m, AffExpr, MOI.EqualTo{Float64}) + num_constraints(m, AffExpr, MOI.GreaterThan{Float64}) + num_constraints(m, AffExpr, MOI.LessThan{Float64}))
end

println("RESULTADO INTEIRO = ", objective_value(m))
println("VARIABLES = ", num_variables(m))
println("CONSTRAINTS = ", num_constraints(m, AffExpr, MOI.EqualTo{Float64}) + num_constraints(m, AffExpr, MOI.GreaterThan{Float64}) + num_constraints(m, AffExpr, MOI.LessThan{Float64}))

#=
for i in ALOCADO_GERAL
    var = X[i]
    if value(var) > 0
        println(var, " ", value(var))
    end
end

for i in ALOCADO_MISSAO
    var = Y[i]
    if value(var) > 0
        println(var, " ", value(var))
    end
end


m1 = Model(Gurobi.Optimizer);

set_time_limit_sec(m1, 600)

@variable(m1, 0 <= X1[ALOCADO_GERAL] <= 1);
@variable(m1, 0 <= Y1[ALOCADO_MISSAO] <= 1);

@objective(m1, Min, sum(2*X1[i]*CUSTO_TRANSPORTE[TRANSPORTE(i.o,i.d)] for i in ALOCADO_GERAL));

@constraint(m1, [d in 1:size(DEM,1)], sum(Y1[j] for j in ALOCADO_MISSAO if j.m == DEM[d,1]) == DEM[d,5]);

@constraint(m1, TEMPO_RESTRICAO[pp in PD[:,1]], sum(Y1[j]*TEMPO_MISSAO[j.m] for j in ALOCADO_MISSAO if j.p == pp) + 
        sum(2 * X1[i] * TEMPO_TRANSPORTE[TRANSPORTE(i.o,i.d)] for i in ALOCADO_GERAL if i.p == pp) <= DISPONIBILIDADE[pp]);

@constraint(m1, [j in ALOCADO_MISSAO], X1[ALOCADO(j.p, j.o, j.d)] >= Y1[j]);

optimize!(m1)


for i in Y
    if value(i) > 0.1
        println(i, " ", value(i))
    end
end


RESPOSTA = []
for (index, i) in enumerate(Y)
    if value(i) > 0
        println(i, " ", value(i))
        push!(RESPOSTA, index)
    end
end

R_OD = []
R_P_OD = []
R_ALOC = []
R_TEMPO_ATIVIDADE = []
for r in ALOCADO_MISSAO[RESPOSTA]
    push!(R_OD, [r.o, r.d])
    push!(R_P_OD, ALOCADO(r.p, r.o, r.d))
    push!(R_ALOC, r.p)
    push!(R_TEMPO_ATIVIDADE, TEMPO_MISSAO[r.m])
end


R_P_OD_UNICOS = unique(R_P_OD)
R_ALOC_UNICOS = unique(R_ALOC)

l = []
for a in R_P_OD_UNICOS
    push!(l, a.p)
end

t = []
for p in R_ALOC_UNICOS
    push!(t, sum(l[:,1] .== p))
end


sort!(t, rev = true)

R_ALOC_TRANSP_TEMPO = [TEMPO_TRANSPORTE[TRANSPORTE(p.o, p.d)] for p in R_P_OD_UNICOS]

R_QTD_ALOC = [sum(R_ALOC .== i) for i in R_ALOC_UNICOS]

R_TOTAL_TEMPO_ATIVIDADE = [value(TEMPO_RESTRICAO[i]) for i in R_ALOC_UNICOS]

R_MATRIZ = hcat(R_ALOC_UNICOS, R_QTD_ALOC, R_TOTAL_TEMPO_ATIVIDADE)

R_MATRIZ = sort(R_MATRIZ, dims = 1, rev = true)

=#