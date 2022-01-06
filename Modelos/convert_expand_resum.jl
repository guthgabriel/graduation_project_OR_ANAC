using XLSX
using DataFrames

arquivo = XLSX.readxlsx("Instancia/InstanciaB3.xlsx")

PERIODOS = 1

# SETS
    # Pessoa
P = pessoas = arquivo["Disponibilidade - PREENCHER!A3:A179"] #arquivo["pessoas"]
POD = reshape(arquivo["Disponibilidade - PREENCHER!A3:D179"], (:,4))

    # Origem
origem = arquivo["origem"]
origemativa = arquivo["origemativa"]
O = origem[origemativa .> 0]
PO = arquivo["Disponibilidade - PREENCHER!A3:B179"] #arquivo["PO"]

destino = arquivo["destino"]
destinoativo = arquivo["destinoativo"]
DA = destino[destinoativo .> 0]

arcotransporte = arquivo["arcotransporte"]

nos = arquivo["nos"]

missao = arquivo["Demanda - PREENCHER!B3:B102"] #arquivo["missao"]
grupo = arquivo["grupo"]
pessoaquebrada = arquivo["pessoaquebrada"]

# PARAMETROS
custo = arquivo["custo"]
OD = arquivo["OD"]
arco = arquivo["arco"]
disponibilidade = arquivo["Disponibilidade - PREENCHER!D3:D179"] # arquivo["disponibilidade"]
duracao = arquivo["duracao"]
equipe = arquivo["equipe"]

tempo = arquivo["tempo"]
grupoativo = arquivo["grupoativo"]

atividades = arquivo["atividades"]

ExisteMissao = arquivo["Demanda - PREENCHER!B3:C102"] #arquivo["ExisteMissao"]
dem = arquivo["Demanda - PREENCHER!B3:D102"] #arquivo["dem"];
missoes_ativas = dem
missao_destinos = unique(missoes_ativas[:,2:3], dims=1) # CUIDADO - PODE EXISTIR MAIS DE UMA MISSAO PARA O MESMO DESTINO

tempo_missao = Float64[]
equipe_missao = Int64[]

OD_ativos = filter(x -> OD[x,1] in O && OD[x,2] in DA, 1:length(OD[:,1]))
OD_ativos = OD[OD_ativos, 1:2]

for m in 1:size(dem, 1)
    push!(tempo_missao, atividades[atividades[:,1] .== dem[m,2], 2][1])
    push!(equipe_missao, atividades[atividades[:,1] .== dem[m,2], 3][1])
end

demanda_missao = hcat(dem, tempo_missao, equipe_missao)

pessoa_ativa = []
lgt = []
for i in 1:size(PO,1), da in DA, j in 1:size(OD,1)
    if da == OD[j,2]
        atividades = missao_destinos[missao_destinos[:,2] .== da,1]
        if length(intersect(atividades, pessoaquebrada[pessoaquebrada[:,1] .== PO[i,1],2])) > 0 && PO[i,2] == OD[j,1]
        #println(locadogeralteste(PO[i,1],PO[i,2], da))
            push!(lgt, PO[i,1],PO[i,2], da)
            push!(pessoa_ativa, PO[i,1])
        end
    end
end
#=
for i in 1:size(PO,1), da in DA
    atividades = missao_destinos[missao_destinos[:,2] .== da,1]
    if length(intersect(atividades, pessoaquebrada[pessoaquebrada[:,1] .== PO[i,1],2])) > 0
    #println(locadogeralteste(PO[i,1],PO[i,2], da))
        push!(lgt, PO[i,1],PO[i,2], da)
        push!(pessoa_ativa, PO[i,1])
    end
end
=#
unique!(pessoa_ativa)

indice_ativos = filter(x -> POD[x,1] in pessoa_ativa, 1:length(pessoas))
tempo_disponivel = POD[indice_ativos,4]

lgt = permutedims(reshape(lgt, 3,:))

pessoa = Dict{String, Array}()
missoes_ativas_unicas = unique(missoes_ativas[:,2])
for i in missoes_ativas_unicas
    pessoa[i] = pessoaquebrada[pessoaquebrada[:,2] .== i,1]
end

#OD_ativos = unique(lgt[:,2:3],dims=1)

lt = []
for i in 1:size(lgt,1)
    atividades = missoes_ativas[missoes_ativas[:,3] .== lgt[i,3],1:2]
    for at in atividades[:,1]
        temp = atividades[atividades[:,1] .== at,1]
        temp2 = atividades[atividades[:,1] .== at,2]
        if length(temp) == 1
            temp = temp[1]
            temp2 = temp2[1]
            if lgt[i,1] in pessoa[temp2]
                push!(lt, lgt[i,1],lgt[i,2],lgt[i,3],string(temp))
            end
        end
    end
end

lt = permutedims(reshape(lt, 4,:))


indice_arcos_ativos = filter(x -> arcotransporte[x,1] in OD_ativos[:,1] && arcotransporte[x,2] in OD_ativos[:,2], 1:size(arcotransporte,1))

custo_viagem = arcotransporte[indice_arcos_ativos, 3]
tempo_viagem = arcotransporte[indice_arcos_ativos, 4]
OD_viagem = arcotransporte[indice_arcos_ativos, 1:2]

OM_viagem = unique(lt[:,2:4],dims=1)
custo_m_viagem = []
tempo_m_viagem = []


XLSX.openxlsx("Instancia/InstanciaB3_resum.xlsx", mode="w") do xf
    sheet = xf[1]
    XLSX.rename!(sheet, "DADOS")

    sheet["A1"] = ["MISSAO1", "ATIVIDADE", "DESTINO1", "DURACAO", "EQUIPE"]
    sheet["A2"] = demanda_missao

    sheet["G1"] = ["PESSOA1"]
    sheet["G2", dim=1] = pessoa_ativa

    sheet["H1"] = ["DISPONIBILIDADE"]
    sheet["H2", dim=1] = tempo_disponivel

    sheet["J1"] = ["ORIGENS"]
    sheet["J2", dim=1] = O

    sheet["K1"] = ["DESTINOS"]
    sheet["K2", dim=1] = DA

    sheet["M1"] = ["ORIGEM2", "DESTINO2"]
    sheet["M2"] = OD_viagem

    sheet["O1"] = ["CUSTO"]
    sheet["O2", dim=1] = custo_viagem

    sheet["P1"] = ["TEMPO"]
    sheet["P2", dim=1] = tempo_viagem

    sheet["R1"] = ["PESSOA3", "ORIGEM3", "DESTINO3"]
    sheet["R2"] = lgt

    sheet["V1"] = ["PESSOA4", "ORIGEM4", "DESTINO4", "MISSAO4"]
    sheet["V2"] = lt

end
