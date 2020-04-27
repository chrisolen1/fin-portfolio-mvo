using JuMP, Ipopt, DelimitedFiles

# estimated returns

mu = readdlm("tmp/mu.txt")

# var-cov matrix

sigma = readdlm("tmp/sigma.txt")

# risk aversion

delta = readdlm("tmp/delta.txt")[1]

# minimum allowable weight

min_weight = readdlm("tmp/min_weight.txt")[1]

# number of assets

n,k = size(sigma)

# initialize model
model = Model(with_optimizer(Ipopt.Optimizer))

# weights must be >= min_weight the volume of the portfolio
@variable(model, x[1:n]>=min_weight) 

# define objective function
@NLobjective(model, Max, sum(mu[i]*x[i] for i=1:n) - ((delta*1/2)*sum(x[i]*sigma[i,j]*x[j] for i=1:n for j=1:n))) 

# weights must sum up to one
@NLconstraint(model, sum(x[i] for i=1:n)==1)                

# run optimizer

JuMP.optimize!(model)

# extract weight variables

weights = JuMP.value.(x)

# write weight variables to txt

outfile = "tmp/weights.txt"
open(outfile, "w") do f
  for i in weights
    println(f, i)
  end
end 
