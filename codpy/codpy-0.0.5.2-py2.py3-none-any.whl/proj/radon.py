from preamble import * 
import pydicom 
from data_generators import * 
from predictors import *

import numpy as np
import matplotlib.pyplot as plt

from skimage import io,transform
from skimage.data import shepp_logan_phantom
from skimage.transform import radon, rescale

def _iradon(sng, max_iter= 2,**kwargs):
      from skimage.transform import iradon_sart
      rescale =  bool(kwargs.get("inv_radon_rescale",False))

      img = iradon_sart(sng)
      for n in range(max_iter):
            img = iradon_sart(sng, image=img)
      if rescale: img *= 255./ img.max()
      return img 

def _radon(img, **kwargs):
      from skimage.transform import iradon_sart
      theta =  kwargs.get("theta",[])
      circle =  bool(kwargs.get("circle",True))
      if len(theta): img = radon(image=img, theta = theta, circle = circle)
      else: img = radon(image=img)
      return img 


def test_radon(image = [], **kwargs):
      from skimage import io
      image_path = kwargs.get("image_path",[])
      if not len(image) and len(image_path): test_radon(image = io.imread(image_path))
      fig, (ax1, ax2, ax3, ax4,ax5) = plt.subplots(1, 5, figsize=(8, 4.5))
      ax1.imshow(image)
      test1 = _iradon(sng = _radon(img = image, **kwargs),**kwargs)
      ax2.imshow(test1)
      test2 = test1-image
      ax3.imshow(test2)
      test3 = _iradon(sng = _radon(img = test1, **kwargs),**kwargs)
      ax4.imshow(test3)
      test4 = test3-test1
      ax5.imshow(test4)
      plt.show()
      pass


class dicom_interface:

    def __init__(self,**kwargs):
        currentdir = os.path.dirname(os.path.realpath(__file__))
        bdd_path = os.path.join(currentdir,"BDD")
        list_dicom_path = files_indir(bdd_path,extension = "dcm")
        imgs = dicom_interface.load_images(list_dicom_path)
        save_path = os.path.join(currentdir,"sav")
        if not os.path.isdir(save_path): os.mkdir(save_path)
        save_paths = []
        [save_paths.append(save_path) for n in range(len(imgs))]

        list_saved_png = files_indir(save_path,extension = "png")
        [os.remove(p) for p in list_saved_png]
        [dicom_interface.save_images(list_imgs,dicom_path,save_path) for list_imgs,dicom_path,save_path in zip(imgs,list_dicom_path,save_paths)]


    def separate_images(pydicomimgs):
        test = pydicomimgs.pixel_array
        return [test[n] for n in range(len(test))]
        pass

    def load_images(list_path):
        from skimage import io
        return [dicom_interface.separate_images(pydicom.dcmread(p)) for p in list_path]

    def get_fig_name(base_path,n):
        return base_path+str(n)+".png"


    def save_images(list_imgs,dicom_path,save_path):
        from skimage import io
        base_path = os.path.basename(dicom_path)
        base_path = os.path.join(save_path,base_path)
        len_ = len(list_imgs)
        if len_ == 120 : len_=60
        for n in range(len_):
            test = list_imgs[n].copy().astype(float)
            max_ = test.max()
            test *= 255/int(max_)
            io.imsave(get_fig_name(base_path,n),test) 
        # return [io.imsave(get_fig_name(base_path,n),list_imgs[n]) for n in range(len(list_imgs))]



class graphical_radon_utilities:
      def plot_original(predictor ,ax, **kwargs):
            ax.set_title("Original")
            ax.imshow(predictor.generator.image, cmap=plt.cm.Greys_r)
      def plot_reconstructed(predictor ,ax, **kwargs):
            ax.set_title("rec : "+predictor.id())
            ax.imshow(predictor.f_z, cmap=plt.cm.Greys_r)
      def plot_error(predictor ,ax, **kwargs):
            ax.set_title("error:"+predictor.id())
            ax.imshow(predictor.f_z - predictor.generator.image, cmap=plt.cm.Greys_r)
      def plot_sinogram(predictor ,ax, **kwargs):
            ax.set_title("Sinogram")
            ax.set_title("Radon transform\n(Sinogram)")
            ax.set_xlabel("Projection angle (deg)")
            ax.set_ylabel("Projection position (pixels)")
            dx, dy = 0.5 * 180.0 / max(predictor.generator.image.shape), 0.5 / predictor.generator.sinogram.shape[0]
            ax.imshow(predictor.generator.sinogram, cmap=plt.cm.Greys_r,extent=(-dx, 180.0 + dx, -dy, predictor.generator.sinogram.shape[0] + dy),aspect='auto')

class generate_sngdata:
      ntheta = 8
      def __init__(self,dir_rsc='',dir_img='',dir_sng='',dir_x='',dir_fx='',dir_z='',dir_fz='',**kwargs):
            self.theta =  kwargs.get("theta",[])
            self.rsc =  kwargs.get("rsc",.5)
            if not len(self.theta): self.theta = np.arange(start = 0, stop = 180, step= int(180/self.ntheta))

            currentdir = os.path.dirname(os.path.realpath(__file__))
            if not len(dir_img): self.dir_img = os.path.join(currentdir,'img')
            else: self.dir_img = dir_img
            if not len(dir_rsc): self.dir_rsc = os.path.join(currentdir,'rsc')
            else: self.dir_rsc = dir_rsc
            if not len(dir_sng): self.dir_sng = os.path.join(currentdir,'sng')
            else: self.dir_sng = dir_sng
            if not len(dir_x): self.dir_x = os.path.join(currentdir,'train.x')
            else: self.dir_x = dir_x
            if not len(dir_fx): self.dir_fx = os.path.join(currentdir,'train.fx')
            else: self.dir_fx = dir_fx
            if not len(dir_z): self.dir_z = os.path.join(currentdir,'test.z')
            else: self.dir_z = dir_z
            if not len(dir_fz): self.dir_fz = os.path.join(currentdir,'test.fz')
            else: self.dir_fz = dir_fz

            if not os.path.isdir(self.dir_rsc): os.mkdir(self.dir_rsc)
            if not os.path.isdir(self.dir_sng): os.mkdir(self.dir_sng)
            if not os.path.isdir(self.dir_x): os.mkdir(self.dir_x)
            if not os.path.isdir(self.dir_z): os.mkdir(self.dir_z)
            if not os.path.isdir(self.dir_fx): os.mkdir(self.dir_fx)
            if not os.path.isdir(self.dir_fz): os.mkdir(self.dir_fz)


            self.list_rsc=files_indir(self.dir_rsc,".png")
            self.list_img=files_indir(self.dir_img,".png")
            self.list_sng=files_indir(self.dir_sng,".png")
            if len(self.list_rsc): self.img_shape = np.asarray(io.imread(self.list_rsc[0])).shape
            self.list_x=files_indir(self.dir_x,".png")
            self.list_fx=files_indir(self.dir_fx,".png")
            self.list_z=files_indir(self.dir_z,".png")
            if len(self.list_rsc):  self.sinogram_shape = [self.img_shape[0],len(self.theta)]
            self.list_fz=files_indir(self.dir_fz,".png")


            self.rsc_path=os.path.join(self.dir_rsc,'rsc.npy')
            self.sng_path=os.path.join(self.dir_sng,'sng.npy')
            self.img_path=os.path.join(self.dir_img,'img.npy')
            self.fx_path=os.path.join(self.dir_fx,'fx.npy')
            self.x_path=os.path.join(self.dir_x,'x.npy')
            self.fz_path=os.path.join(self.dir_fz,'fz.npy')
            self.z_path=os.path.join(self.dir_z,'z.npy')
            pass   

      def generate_set(self,**kwargs):
            if bool(kwargs.get("gen_rsc",False)): 
                  [os.remove(p) for p in self.list_rsc]
                  self.generate_data_set()
                  self.list_rsc=files_indir(self.dir_rsc,".png")

            if bool(kwargs.get("gen_sng",False)): 
                  [os.remove(p) for p in self.list_sng]
                  self.generate_all_sinograms()
                  self.list_sng=files_indir(self.dir_sng,".png")
            if bool(kwargs.get("gen_img",False)):
                  out = np.vstack([self.load_array(p) for p in self.list_img])
                  if os.path.exists(self.img_path):os.remove(self.img_path)
                  np.save(self.img_path,out)

      def load_array(self,path):
            fx = np.asarray(io.imread(path))
            return [fx.flatten()]

      def generate_data_set(self):
            imgs = self.load_images()
            imgs = parallel_task(imgs, self.rescale_img)
            imgs = parallel_task(imgs, self.iradon_radon)
            [self.save_img(img,path) for img,path in zip(imgs,self.list_img)]
            imgs = np.vstack([img.flatten() for img in imgs])
            if os.path.exists(self.rsc_path):os.remove(self.rsc_path)
            np.save(self.rsc_path,imgs)


      def load_images(self):
            from skimage import io
            return [io.imread(p) for p in self.list_img]

      def rescale_img(self,img):
            return transform.rescale(img, self.rsc, anti_aliasing=False)

      def iradon_radon(self,img):
            print('#', end='')
            return _iradon(sng = _radon(img = img))

      def save_img(self,img,image_path):
            from skimage import io
            fig_name = os.path.basename(image_path)
            fig_name = os.path.join(self.dir_rsc,fig_name)
            io.imsave(fig_name,img)


      def generate_all_sinograms(self):
            imgs = np.load(self.rsc_path)
            imgs = parallel_task([imgs[n] for n in range(len(imgs)) ],self.gen_sinogram_from_array)
            paths = [os.path.join(self.dir_sng,os.path.basename(p)) for p in self.list_rsc]
            [io.imsave(path,img) for path,img in zip(paths,imgs)]
            imgs = np.vstack([img.flatten() for img in imgs])
            if os.path.exists(self.sng_path):os.remove(self.sng_path)
            np.save(self.sng_path,imgs)


      def gen_sinogram_from_array(self,img_array):
            from skimage import io
            sinogram = _radon(img = img_array.reshape(self.img_shape), theta=self.theta)
            return sinogram

      def save_rescale(self,image_path):
            from skimage.transform import rescale
            from skimage import io
            from sklearn import preprocessing
            fig_name = os.path.basename(image_path)
            fig_name = os.path.join(self.dir_rsc,fig_name)
            io.imsave(fig_name,rescale(io.imread(image_path), self.rsc, anti_aliasing=False))



class radon_generator(data_generator,graphical_radon_utilities):
      def __init__(self,D=0,Nx=0,Ny=0,Nz=0,**kwargs):
            super().__init__(D,Nx,Ny,Nz,**kwargs)
            self.image =  kwargs.get("image",[])
            self.theta =  kwargs.get("theta",[])
            if len(self.theta)*len(self.image): 
                  self.sinogram = _radon(image = self.image, theta=self.theta)
                  self.pixels = np.arange(start = 0, stop = 1., step = 1./self.sinogram.shape[1])
            else: self.sinogram = []
            

      def get_raw_data(self,Nx, Ny, Nz, D,**kwargs):
            import itertools as it
            x = tuple(it.product(self.theta, self.pixels))
            map(lambda a:  [a[1]*np.cos(a[0]),a[1]*np.sin(a[0])], x)
            x = np.reshape(x,(len(x),D))
            x,y,z,fx,fz = x,[],x,self.sinogram,self.image
            return (x,y,z,fx,fz,1, -1, 1)

      def get_data(self,D=0,Nx=0,Ny=0,Nz=0,**kwargs):
            if (D*Nx*Ny*Nz):
                  x,y,z,fx,fz,Nx, Ny, Nz = self.get_raw_data(Nx,Ny,Nz,D,**kwargs)
            return  x, fx, y, [], z, fz
      def copy(self):
            return self.copy_data(radon_generator())


class sub_radon_generator(data_generator,graphical_radon_utilities):
      x_,fx_,z_,fz_,generate_sngdata_ =[],[],[],[],[]
      def __init__(self,D=0,Nx=0,Ny=0,Nz=0,**kwargs):
            super().__init__(D,Nx,Ny,Nz,**kwargs)
      
      def load(self,**kwargs):
            self.generate_sngdata_ = generate_sngdata(**kwargs)
            self.img_shape = self.generate_sngdata_.img_shape
            self.sinogram_shape = self.generate_sngdata_.sinogram_shape
            self.theta = self.generate_sngdata_.theta
            # self.img_ = np.load(self.generate_sngdata_.img_path)
            self.rsc_ = np.load(self.generate_sngdata_.rsc_path)
            self.sng_ = np.load(self.generate_sngdata_.sng_path)
            self.fx_ = self.rsc_[0:len(self.rsc_)-28]
            self.x_ = self.sng_[0:len(self.rsc_)-28]
            self.fz_ = self.rsc_[len(self.rsc_)-29:]
            self.z_ = self.sng_[len(self.rsc_)-29:]
      
      def get_data(self,D=0,Nx=0,Ny=0,Nz=0,**kwargs):
            if (D*Nx*Ny*Nz):
                  if not(len(self.x_)):self.load(**kwargs)
                  return  self.x_, self.fx_, self.x_, [], self.z_, self.fz_
      def copy(self):
            out = super().copy_data(sub_radon_generator())
            out.generate_sngdata_ = self.generate_sngdata_
            out.fx_ = self.fx_
            out.x_ = self.x_
            out.fz_ = self.fz_
            out.z_ = self.z_

class sub_radon_generator_sinc(sub_radon_generator):

      def load(self):
            import itertools as it
            super().load()
            length = 1.
            step = length/self.generate_sngdata_.img_shape[1]
            pixels = np.arange(start = -length, stop = length, step = 2.*step)
            theta = np.arange(start = step/2., stop = 1., step = 1./self.generate_sngdata_.sinogram_shape[1])
            self.grid_x_ = tuple(it.product(pixels,theta))
            self.grid_x_ = list(map(lambda a:  [a[0]*np.cos(a[1]*np.pi),a[0]*np.sin(a[1]*np.pi )], self.grid_x_))
            self.grid_x_ = np.reshape(self.grid_x_,(len(self.grid_x_),2))

            step = 1./self.generate_sngdata_.img_shape[1]
            theta = np.arange(start = 0., stop = 1., step = step)
            self.grid_z_ = tuple(it.product(pixels,theta))
            self.grid_z_ = list(map(lambda a:  [a[0]*np.cos(a[1]*np.pi),a[0]*np.sin(a[1]*np.pi )], self.grid_z_))
            self.grid_z_ = np.reshape(self.grid_z_,(len(self.grid_z_),2))


            # self.fx_ = np.load(self.generate_sngdata_.z_path).T.astype(float)
            # self.fz_ = np.load(self.generate_sngdata_.fz_path).astype(float)
      
      def get_data(self,D=0,Nx=0,Ny=0,Nz=0,**kwargs):
            if (D*Nx*Ny*Nz):
                  if not(len(self.x_)):self.load()
                  return  self.x_, self.fx_, self.x_, [], self.z_, self.fz_

class radon_predictor(data_predictor):
      def predictor(self,**kwargs):
            pass
      
      def copy(self):
            return self.copy_data(radon_predictor())
      def id(self,name = ""):
            return name

class sub_radon_predictor(codpyexRegressor):

      def __init__(self,**kwargs):
            super().__init__(**kwargs)
            self.sub_radon_generator_sinc_= sub_radon_generator_sinc(**kwargs)
      def radon_array(self,arr):
            return _radon(img = arr.reshape(self.generator.img_shape), theta=self.generator.theta).flatten()
      def iradon_array(self,arr):
            from skimage.transform import iradon
            if len(arr) == self.generator.sinogram_shape[0]* self.generator.sinogram_shape[1]:return _iradon(sng = arr.reshape(self.generator.sinogram_shape)).flatten()
            if len(arr) == self.generator.img_shape[0]* self.generator.img_shape[1]:return _iradon(sng = arr.reshape(self.generator.img_shape)).flatten()

      def predictor(self,**kwargs):
            if (self.D*self.Nx*self.Ny*self.Nz ):
                  self.f_z = op.projection(x = self.x,y = self.x,z = self.z, fx = self.fx,set_codpy_kernel=self.set_kernel,rescale = True,**kwargs)
            pass

      
      def copy(self):
            return self.copy_data(sub_radon_predictor())

      def id(self,name = ""):
            return "sub_radon_predictor"

class sub_radon_predictor_SART(sub_radon_predictor):
      def predictor(self,**kwargs):
            if (self.D*self.Nx*self.Ny*self.Nz ):
                  self.f_z = parallel_task([self.z[n] for n in range(len(self.z))],self.iradon_array) 
                  self.f_z = np.vstack([p.flatten() for p in self.f_z])

     
      def copy(self):
            return self.copy_data(sub_radon_predictor_SART())
      def id(self,name = ""):
            return "SART"


class sub_radon_predictor_SART_extra(sub_radon_predictor):
      set_sinc_kernel = kernel_setters.kernel_helper(kernel_setters.set_sincardtensor_kernel, 0,1e-8,map_setters.set_min_distance_map)
      set_mat_kernel = kernel_setters.kernel_helper(kernel_setters.set_matern_tensor_kernel, 2,1e-8,map_setters.set_mean_distance_map)

      def predictor(self,**kwargs):
            if (self.D*self.Nx*self.Ny*self.Nz ):
                  # multi_plot([[self.generator.grid_x_,self.z[0]]], fun_plot = plotD, projection='3d')
                  self.f_z = op.projection(x = self.generator.grid_x_,y = self.generator.grid_x_,z = self.generator.grid_z_, fx = self.z.T.copy(),set_codpy_kernel=self.set_mat_kernel,rescale = True,**kwargs).T 
                  # multi_plot([[self.generator.grid_z_,self.f_z[0]]], fun_plot = plotD, projection='3d')
                  self.f_z = parallel_task([self.f_z[n] for n in range(len(self.f_z))],self.iradon_array) 
                  self.f_z = np.vstack(self.f_z)
                  # self.f_z = self.fz.copy()

     
      def copy(self):
            return self.copy_data(sub_radon_predictor_SART_extra())
      def id(self,name = ""):
            return "SART_extra"

class sub_radon_predictor_exact(sub_radon_predictor):
      def predictor(self,**kwargs):
            if (self.D*self.Nx*self.Ny*self.Nz ):
                  self.f_z = self.fz.copy()
     
      def copy(self):
            return self.copy_data(sub_radon_predictor_exact())
      def id(self,name = ""):
            return "exact"

class sub_radon_predictor_back(sub_radon_predictor):
      set_gaussian_kernel = kernel_setters.kernel_helper(kernel_setters.set_gaussian_kernel, 0,0 ,map_setters.set_mean_distance_map)
      set_sinc_kernel = kernel_setters.kernel_helper(kernel_setters.set_sincardtensor_kernel, 0,1e-8 ,None)
      set_mat_kernel = kernel_setters.kernel_helper(kernel_setters.set_matern_tensor_kernel, 0,0 ,map_setters.set_mean_distance_map)
      set_matnorm_kernel = kernel_setters.kernel_helper(kernel_setters.set_matern_norm_kernel, 0,0 ,map_setters.set_mean_distance_map)
      set_linear_kernel = kernel_setters.kernel_helper(kernel_setters.set_linear_regressor_kernel, 2,0 ,None)

      def __init__(self,**kwargs):
            self.name = kwargs.get("name","codpy")
            super().__init__(**kwargs)

      def predictor(self,**kwargs):
            if (self.D*self.Nx*self.Ny*self.Nz ):
                  self.f_z = op.projection(x = self.x,y = self.x,z = self.z, fx = self.fx,set_codpy_kernel=self.set_matnorm_kernel,rescale = True,**kwargs)
                  err = parallel_task([self.f_z[n] for n in range(len(self.f_z))],self.radon_array) 
                  err = np.vstack([p.flatten() for p in err])
                  next_ = self.z-err
                  err = parallel_task([next_[n] for n in range(len(next_))],self.iradon_array)
                  err = np.vstack([p.flatten() for p in err])
                  self.f_z += err
                  # err = op.projection(x = self.x,y = self.x,z = next_, fx = self.fx,set_codpy_kernel=set_matnorm_kernel,rescale = True,**kwargs)
                  # err = parallel_task([err[n] for n in range(len(err))],self.radon_array) 
                  # err = np.vstack([p.flatten() for p in err])
                  # err = next_-err
                  # err = parallel_task([err[n] for n in range(len(err))],self.iradon_array)
                  # err = np.vstack([p.flatten() for p in err])
                  # self.f_z += err

     
      def copy(self):
            return self.copy_data(sub_radon_predictor_back())
      def id(self,name = ""):
            return self.name

class Filtered_Back_Projection_predictor(radon_predictor):
      def __init__(self,**kwargs):
            super().__init__(**kwargs)
            self.filter = kwargs.get("filter",'ramp')
            pass


      def predictor(self,**kwargs):
            from skimage.transform import iradon
            self.f_z = iradon(self.generator.sinogram, theta=self.generator.theta, filter_name=self.filter)
      
      def copy(self):
            return self.copy_data(Filtered_Back_Projection_predictor(filter = self.filter))
      def id(self,name = ""):
            return "FBP "+self.filter

class Algebraic_Reconstruction_predictor(radon_predictor):
      def __init__(self,**kwargs):
            super().__init__(**kwargs)
            self.iteration = kwargs.get("iteration",1)
            pass
      def predictor(self,**kwargs):
            from skimage.transform import iradon_sart
            self.f_z = iradon_sart(self.generator.sinogram, theta=self.generator.theta)
            for n in range(self.iteration):
                  self.f_z = iradon_sart(self.generator.sinogram, theta=self.generator.theta, image=self.f_z)
      def copy(self):
            return self.copy_data(Algebraic_Reconstruction_predictor(iteration = self.iteration))
      def id(self,name = ""):
            return "AR :"+str(self.iteration)

class codpy_radon_predictor(radon_predictor):
      def predictor(self,**kwargs):
          coefficients = op.coefficients(self.x,self.y,self.fx,set_kernel = self.kernel, rescale = True)
      def copy(self):
            return self.copy_data(codpy_radon_predictor(iteration = self.iteration))
      def id(self,name = ""):
            return "codpy"

def utilfzs(list_fzs,img_shape):
      fzs = list_fzs[0]
      test = len(fzs)
      out= []
      for fzs in list_fzs:
            if len(out)==0: [out.append([fzs[n].reshape(img_shape)]) for n in range(len(fzs))]
            else: 
                  for outit,n in zip(out,range(len(fzs))): 
                        outit.append(fzs[n].reshape(img_shape)) 
      return out


def sub_radon_impl(**kwargs):
      scenarios_list = [ (-1, -1, -1, -1 ) ]
      scenario_generator_,data_accumulator_ = scenario_generator(),data_accumulator(**kwargs)
      # generator_,predictor_ = sub_radon_generator(**kwargs),sub_radon_predictor(**kwargs)
      # validator_compute=['accuracy_score','discrepancy_error','norm_function']
      validator_compute=['accuracy_score']
      scenario_generator_.run_scenarios(scenarios_list,sub_radon_generator(**kwargs),sub_radon_predictor_exact(**kwargs),data_accumulator_,validator_compute = validator_compute,**kwargs)
      # scenario_generator_.run_scenarios(scenarios_list,sub_radon_generator_sinc(**kwargs),sub_radon_predictor_SART_extra(**kwargs),data_accumulator_,validator_compute = validator_compute,**kwargs)

      scenario_generator_.run_scenarios(scenarios_list,sub_radon_generator(**kwargs),sub_radon_predictor_SART(**kwargs),data_accumulator_,validator_compute = validator_compute,**kwargs)
      # scenario_generator_.run_scenarios(scenarios_list,sub_radon_generator(**kwargs),sub_radon_predictor(**kwargs),data_accumulator_,validator_compute = validator_compute,**kwargs)
      scenario_generator_.run_scenarios(scenarios_list,sub_radon_generator(**kwargs),sub_radon_predictor_back(**kwargs),data_accumulator_,validator_compute = validator_compute,**kwargs)

      results = scenario_generator_.accumulator.get_output_datas().dropna(axis=1)
      print(results)
      fzs = utilfzs(data_accumulator_.get_f_zs(),scenario_generator_.data_generator.img_shape)
      multi_plot(fzs,show_imgs,**kwargs,mp_max_items=8)
      # predictor_.compare_test_img()

def radon_impl(**codpy_param):
      image = shepp_logan_phantom()
      image = rescale(image, scale=0.4, mode='reflect')
      ntheta = int(codpy_param.get('ntheta',180))

      theta = np.linspace(0., 180., min( (ntheta,max(image.shape)) ), endpoint=False)
      radon_generator_ = radon_generator(image = image, theta = theta)

      scenario_generator_,data_accumulator_ = scenario_generator(),data_accumulator()
      filters = ['ramp', 'shepp-logan', 'cosine', 'hamming', 'hann']

      scenarios_list = [ (-1, -1, -1, -1 ) ]
      validator_compute=['accuracy_score','discrepancy_error','norm_function']
      for filter in filters:
            scenario_generator_.run_scenarios(scenarios_list,radon_generator_,Filtered_Back_Projection_predictor(filter = filter),data_accumulator_,validator_compute = validator_compute,**kwargs)

      for iteration in range(0,3):
            scenario_generator_.run_scenarios(scenarios_list,radon_generator_,Algebraic_Reconstruction_predictor(iteration = iteration),data_accumulator_,validator_compute = validator_compute,**kwargs)

      scenario_generator_.run_scenarios(scenarios_list,radon_generator_,Algebraic_Reconstruction_predictor(iteration = iteration),data_accumulator_,validator_compute = validator_compute,**kwargs)
      results = scenario_generator_.accumulator.get_output_datas().dropna(axis=1)
      print(results)

      multi_plot([scenario_generator_.predictor],graphical_radon_utilities.plot_original,mp_max_items = -1)
      multi_plot([scenario_generator_.predictor],graphical_radon_utilities.plot_sinogram,mp_max_items = -1)
      multi_plot(scenario_generator_.accumulator.predictors,graphical_radon_utilities.plot_reconstructed,mp_max_items = -1)
      multi_plot(scenario_generator_.accumulator.predictors,graphical_radon_utilities.plot_error,mp_max_items = -1)

def main_test(**codpy_param):
      sub_radon_impl(**codpy_param)
#     radon_impl(**codpy_param)

if __name__ == "__main__":
      # set_gaussian_kernel = kernel_setters.kernel_helper(kernel_setters.set_gaussian_kernel, 0,0 ,map_setters.set_mean_distance_map)
      # set_sinc_kernel = kernel_setters.kernel_helper(kernel_setters.set_sincardtensor_kernel, 0,1e-8 ,None)
      # set_mat_kernel = kernel_setters.kernel_helper(kernel_setters.set_matern_tensor_kernel, 0,0 ,map_setters.set_mean_distance_map)
      set_matnorm_kernel = kernel_setters.kernel_helper(kernel_setters.set_matern_norm_kernel, 0,0 ,map_setters.set_mean_distance_map)
      

      kwargs = {'rescale:xmax': 1000,
      'rescale:ymax': 1000,
      'rescale:zmax': 1000,
      'rescale:seed':42,
      'sharp_discrepancy:xmax':1000,
      'sharp_discrepancy:seed':30,
      'sharp_discrepancy:itermax':5,
      'discrepancy:xmax':500,
      'discrepancy:ymax':500,
      'discrepancy:zmax':500,
      'discrepancy:nmax':2000,
      'set_kernel':set_matnorm_kernel}
      def produce_SPECT_image():
            sub_radon_generator_ = sub_radon_generator(**kwargs)
            x, fx, x, [], z, fz= sub_radon_generator_.get_data(-1,-1,-1,-1)
            img = fx[6].reshape(sub_radon_generator_.img_shape)
            radon_sub = x[6].reshape(sub_radon_generator_.sinogram_shape)
            radon_img = _radon(img = img)
            multi_plot([img,radon_img,radon_sub],show_imgs,mp_ncols=3)
            plt.show()
      
      # path = generate_sngdata_.list_img[0]
      # theta = generate_sngdata_.theta
      # test_radon(image_path = path)
      # image = shepp_logan_phantom()
      # image = rescale(image, scale=0.4, mode='reflect')      
      # test_radon(image = image)
      # test_radon(image_path = path,theta = theta)
      # generate_sngdata(**kwargs).generate_all_sinograms()
      # generate_sngdata(**kwargs).generate_set(gen_rsc=False,gen_sng=True)
      # pass
      main_test(**kwargs)
      pass