require 'rubygems'
require 'sinatra'
require 'sinatra/mongo'
require 'json'
require 'erb'

set :mongo, 'mongo://localhost/agile_data'

get '/' do
  erb :index
end

get '/sent_counts/:from/:to' do |from, to|
  @data = mongo['sent_counts'].find_one({:from => from, :to => to})
  erb :'partials/table'
end

get '/to_from_subject' do
  @data = mongo['to_from_subject'].find()
  erb :'partials/read_write_emails'
end