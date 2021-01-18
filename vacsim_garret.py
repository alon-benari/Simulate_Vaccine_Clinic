import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Vacsim:
    '''
    covid 19 admin simulation
    '''
    def __init__(self,env, admin_station, verify_station, vac_station, observe_station, checkout_station):
        self.env = env
      
        
        #self.observe_bay = dict()
        self.stations = admin_station # if you have n number of admin_stations chacking in patients you can add n  patient every t minutes to start the day and so on.
        # self.num_served = dict()
        self.total_time = []
        self.recorder = []

        # resources
        self.admin_resource = simpy.Resource(env, capacity = admin_station) # vac admin resource
        self.verify_resource = simpy.Resource(env, capacity = verify_station) # the admin aspect that happens juts before the vaccination
        self. vac_resource = simpy.Resource(env, capacity = vac_station) # actual vaccinating resource
        self.observe_resource = simpy.Resource(env, capacity = observe_station) # observation bay
        self.checkout_resource = simpy.Resource(env, capacity = checkout_station)  # checkout_station resource

    # def plot_result(self):
    #     '''
    #     method to plot run of simulation
    #     '''
        
    #     fig, (ax0,ax1) =  plt.subplots(1,2)
    #     ax0.scatter(self.num_served.keys(),self.num_served.values())
    #     ax0.set_title('number served')

    #     ax1.plot(self.observe_bay.keys(),self.observe_bay.values())
    #     ax1.set_title('observe bay')
    #     plt.show()

# Actual functions the patient undergoes during vaccinations

    def admin_patient(self, patient):
        '''
        The admin work  that goes into the vaccination
        '''
        yield self.env.timeout(self.admin_time())
    

    def verify_patient(self, patient):
        '''
        The admin work  that goes into the vaccination
        '''
        yield self.env.timeout(self.verify_time())


    def vac_patient(self,patient):
        '''
        get patient vaccinated
        '''
        yield self.env.timeout(self.vac_time())


    def observe_patient(self, patient):
        '''
        observe patient in observation bay
        '''
        yield self.env.timeout(self.observe_time())


    def checkout_patient(self, patient):
        '''
        checkout patient
        '''
        yield self.env.timeout(self.checkout_time())
  
# time constants for veterans undergoing 
    def admin_time(self):
        return random.uniform(5,8) 
    
    def verify_time(self):
        return random.uniform(10,15)
    
    def vac_time(self):
        return random.uniform(1,2)
    
    def observe_time(self):
        return random.uniform(15,35) # proportion of short obs VS long obs.
        
    def checkout_time(self):
        return random.uniform(0,1)
    
    
    def get_df(self):
        '''
        return a dataframe from recorder
        '''
        return  pd.DataFrame(self.recorder ,columns = ["t_out","t_in","patient","users","capacity","queue","state"])
   

    def get_vaccinated(self,env,patient):
        
        arrival_time0 =  env.now
        with self.admin_resource.request() as req: # checkin
            # print('{patient} @admin at {arrival_time0}'.format(patient=patient, arrival_time0 = arrival_time0))
            yield req
            yield env.process(self.admin_patient(patient))            
            self.recorder.append([env.now, arrival_time0, patient, len(req.resource.users),req.resource.capacity, len(req.resource.queue),'admin'])

        arrival_time1 = env.now
        with self.verify_resource.request() as req: # where the 'chair is'
            # print('{patient} @verify at {arrival_time1}'.format(patient=patient, arrival_time1 = arrival_time1))
            yield req
            yield env.process(self.verify_patient(patient))
            self.recorder.append([env.now, arrival_time1,patient, len(req.resource.users),req.resource.capacity, len(req.resource.queue),'verify'])
           

        arrival_time2 = env.now
        with self.vac_resource.request() as req:
            
            yield req
            yield env.process(self.vac_patient(patient))
            
            self.recorder.append([env.now, arrival_time2,patient, len(req.resource.users),req.resource.capacity, len(req.resource.queue),'vac'])
            
        
        arrival_time3 = env.now
        with self.observe_resource.request() as req:
            
            yield req
            yield env.process(self.observe_patient(patient))
            
            self.recorder.append([env.now, arrival_time3,patient, len(req.resource.users),req.resource.capacity, len(req.resource.queue),'obs'])

        arrival_time4 = env.now
        with self.checkout_resource.request() as req:
            
            yield req
            yield env.process(self.checkout_patient(patient))
           
            self.recorder.append([env.now, arrival_time4,patient, len(req.resource.users),req.resource.capacity, len(req.resource.queue),'checkout'])
        self.total_time.append({patient:arrival_time4-arrival_time0})


def get_visuals(df):
    '''
    get visuals for performance specifically the forming at each point and the efficiency
    '''
    states = ['admin','verify','vac','obs','checkout']
    fig, ax = plt.subplots(5,2, figsize = (12,10))
    zeta_dict = {s: df[df.state == s]['zeta'].to_list() for s in states }
    queue_dict = {s: df[df.state == s]['queue'].to_list() for s in states}
    
    for  i,s in enumerate(states):
        ax[i,0].hist(zeta_dict[s], bins = 10, color = 'blue', alpha = 0.5,label = 'effi')
        ax[i,1].hist(queue_dict[s], bins =10, color = 'red', alpha = 0.5, label = 'queue')
        ax[i,0].set_title(s)
        ax[i,1].set_title(s)
        ax[i,0].legend()
        ax[i,1].legend()
    plt.tight_layout()
    plt.show()
    return zeta_dict,queue_dict

            
def  run_clinic(env,clinic):
    '''
    start vaccinating....
    '''
    # every round 15 minutes
    rate_low = 12/float(clinic.stations)
    rate_up = 17/float(clinic.stations)
    
    for patient in range(clinic.stations):
        env.process(clinic.get_vaccinated(env, patient))

    while True:
        
        yield  env.timeout(random.uniform(rate_low,rate_up))
        patient  +=1
        env.process(clinic.get_vaccinated(env, patient))
    


#setup
random.seed(422)
env = simpy.Environment()
#Loken  2,5,4,6,7
admin_station, verify_station, vac_station, observe_station, checkout_station = 7,9,8,17,5  
# stars 4,6,5,17,9/4,9,6,9,9/7,9,8,17,5 # 4,8,4,10,8#2,4,4,6,5 #2,6,2,10,5 #1,4,4,15,1
clinic =  Vacsim(env, admin_station, verify_station, vac_station, observe_station, checkout_station)
env.process(run_clinic(env,clinic))
env.run(until = 480)
res = pd.DataFrame(clinic.recorder ,columns = ["t_out","t_in","patient","users","capacity","queue","state"])  # this holds the whole cours of the simulation
res['zeta'] = res['users']/res.capacity  #  r zeta is the efficacy
z,q = get_visuals(res) # plot distribution of the efficacy and the queue at each station





        

     