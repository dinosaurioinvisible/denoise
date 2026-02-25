
import os
import logging
import threading
import queue
import uuid
import subprocess
import re, ast, json, glob, platform
from typing import List

import flask
from flask import Flask
import h5py
import numpy as np

# my_platform = "mac" if platform.platform(terse=True).startswith("macOS") else ("windows" if platform.platform(terse=True).startswith("Windows") else None)
my_platform = 'windows' if platform.system() == 'Windows' else 'mac'

def alphanumeric_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key, reverse=True)

##### OS dependent codes #####
def find_executable_path():
    exe_path_dict = {"mac": os.path.join("/Applications", "Igor Pro * Folder", "Igor64.app", "Contents", "MacOS", "Igor64"),
                    "windows": os.path.join("C:", "Program Files", "WaveMetrics", "Igor Pro * Folder", "IgorBinaries_x64", "Igor64.exe")}

    path_candidates = glob.glob(exe_path_dict[my_platform])
    assert len(path_candidates) > 0, "Cannot find Igor Pro"

    exe_path = alphanumeric_sort(path_candidates)[0] # get the newest version
    return exe_path

def execute_command_on_my_platform(command, executable_path):
    if my_platform == "mac":
        subprocess.run([executable_path, "-Q", "-X", command])
    elif my_platform == "windows":
        temp = subprocess.list2cmdline([executable_path, "-Q", "-X"])
        subprocess.run(f"{temp} {command}")

def convert_to_igor_path(path):
    return path.replace(os.path.sep, ":")
##### OS dependent codes #####


class Connection:
    TIMEOUT = 3
    ### security_hole options makes it possible to execute any Python code by HTTP requests. Do not use unless you are sure of it.
    def __init__(self, port=15558, security_hole=True, timeout=3):
        self._app = Flask(__name__)
        self._task_queue = queue.Queue(maxsize=10) # set of (command, uid)
        self._queue = queue.Queue(maxsize=10) # set of (status, uid, data_dict or None)
        self._port = port
        self._registered_functions = {"get": self.get, "put": self.put, "print": print}
        self._basepath = os.getcwd()
        self._executable_path = find_executable_path()
        self._security_hole = security_hole
        self.TIMEOUT = timeout

        self._register_route()
        threading.Thread(target=self._run_server, daemon=True).start()

    def reset(self):
        try:
            self._queue.put_nowait(("error", 0, None))
        except queue.Full:
            pass
        try:
            self._queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self._task_queue.get_nowait()
        except queue.Empty:
            pass

    def __call__(self, commands):
        if isinstance(commands, str):
            commands = [commands]
        for c in commands:
            c = c.replace("'", "\"")
            self.execute_command(c)

    def get(self, wavename):
        uid = uuid.uuid1().hex
        try:
            self._task_queue.put(("get", uid), timeout=self.TIMEOUT)
        except queue.Full:
            return

        self.execute_command(f"PyIgorOutputWave({self._port}, \"{uid}\", \"{wavename}\", \"{self._temp_path(True)}\")")
        result = None
        try:
            reply = self._queue.get(timeout=self.TIMEOUT)
            if reply[0] == "ok":
                assert reply[1] == uid, "Error: Request-response ID does not match."
                result = Wave.from_dict(reply[2])

        except queue.Empty:
            pass
        assert self._task_queue.get_nowait() == ("get", uid)
        return result

    def put(self, wave, wavename="", x0=0, dx=1):
        uid = uuid.uuid1().hex
        try:
            self._task_queue.put(("put", uid), timeout=self.TIMEOUT)
        except queue.Full:
            return
        with h5py.File(self._temp_path(), "w") as f:
            dset = f.create_dataset(uid, data=wave)
        self.execute_command(f"PyIgorLoadWave({self._port}, \"{uid}\", \"{wavename}\", \"{self._temp_path(True)}\", 0)")
        try:
            result = self._queue.get(timeout=self.TIMEOUT)
        except queue.Empty:
            result = None
        assert self._task_queue.get_nowait() == ("put", uid)
        return result

    def _run_server(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        flask.cli.show_server_banner = lambda *args: None
        self._app.run(port=self._port)

    def _register_route(self):
        @self._app.route("/")
        def index():
            return "<p>Bridging Igor and Python</p>"

        @self._app.route("/msg/<string:msg>/<string:uid>")
        def got_message(msg, uid):
            if msg == "get":
                result = self._process_get(uid)
                self._queue.put_nowait(result)
            if msg == "put":
                self._queue.put_nowait(("ok", uid, None))
            if msg == "error":
                self._queue.put_nowait(("error", uid, None))
            return "<p>Bridging Igor and Python</p>"

        @self._app.route("/call/<string:commands>")
        def call_command(commands):
            result_list = []
            p = re.compile(r"([\w]+)\(([^\)]*)\)")
            for command in commands.split(";"):
                try:
                    if self._security_hole:
                        result_list.append(eval(command)) # eval is used to execute any Python code.
                    else:
                        m = re.match(p, command)
                        if m is None:
                            continue
                        fname, args = m.groups()
                        args = ast.literal_eval(f"[{args}]")
                        if fname in self._registered_functions:
                            result_list.append(self._registered_functions[fname](*args))
                except Exception as e:
                    print(e)
                    result_list.append(f"error:{command}")
            return ";".join([str(x) for x in result_list if x is not None])

    def _process_get(self, uid):
        with h5py.File(self._temp_path(), mode="r") as f:
            result_dict = {"array": f[uid][...]}
            attrs = f[uid].attrs
            if "IGORWaveScaling" in attrs:
                result_dict["offsets"] = list(attrs["IGORWaveScaling"][1:, 1])
                result_dict["deltas"] = list(attrs["IGORWaveScaling"][1:, 0])
            else: # IGORWaveScaling is omitted for default parameters
                result_dict["offsets"] = [0.0] * len(result_dict["array"].shape)
                result_dict["deltas"] = [1.0] * len(result_dict["array"].shape)
        return ("ok", uid, result_dict)

    def _temp_path(self, for_igor=False):
        path = os.path.join(self._basepath, f"temp_pyigor_{self._port}.h5")
        if for_igor:
            path = convert_to_igor_path(path)
        return path


    def execute_command(self, command):
        execute_command_on_my_platform(command, self._executable_path)

    def wait_done(self):
        try:
            while True:
                if input("Input q to finish:") == "q":
                    break
        except KeyboardInterrupt:
            pass

    ### Wrapper functions ###
    def function(self, f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        self._registered_functions[f.__name__] = f  # Corrected assignment here
        return wrapper

class Wave:
    def __init__(self, array, offsets: List[float], deltas: List[float], units: str=""):
        if isinstance(array, list):
            array = np.array(array)  # Corrected the input here
        self.array = array
        self.offsets = offsets
        self.deltas = deltas
        self.units = units

    @classmethod
    def from_dict(cls, d):
        wave = Wave(**d)
        return wave

    @property
    def shape(self):
        return self.array.shape

    @property
    def numpnts(self):
        return self.array.size

    @property
    def deltax(self):
        return self.deltas[0]

    @property
    def leftx(self):
        return self.offsets[0]

    def __repr__(self):
        return f"<pyigor.Wave shape: {self.shape}, data_type: {self.array.dtype}, deltas: {self.deltas}, offsets: {self.offsets}>"

def __copy__(self):
    return self.__class__(self.array.copy(), self.offsets[:], self.deltas[:])

def __deepcopy__(self, memo):
    return self.__copy__()

#####################################

array = np.array([0,1,2,3,4])
igor.put(array,"test")

#####################################

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.optimize import minimize_scalar

@igor.function
def BatchModelVarianceWithResponses(cycRFFT, model_input, model_outputName):

    N_average=100
    noise_scales=(1.0,1.5,2.0,3.0)
    k=4
    seed =1

    # r0 inference
    r0_bounds=(0, 50)
    r0_prior_scale=100.0
    n_boot=25
    boot_seed=123

    # DF_r simulation
    amp_nominal=0.15
    sim_reps_per_A_fit=10
    sim_reps_per_A_boot=6

    seed = int(np.abs(hash(cycRFFT)) % (2**32 - 1))
    rng = np.random.default_rng(seed)

    # --------------------------------------------------------------
    # LOAD SUMMARY TABLE
    # --------------------------------------------------------------
    summaryTable = igor.get(f"{model_input}")
    summaryTable = summaryTable.array
    summaryTableDF = pd.DataFrame(summaryTable.reshape((summaryTable.shape[0],summaryTable.shape[1])))
    summary = summaryTableDF.values

    inst_var_point = summary[0,-1]

    # --------------------------------------------------------------
    # LOAD RESPONSES
    # --------------------------------------------------------------
    cycR = igor.get(f"{cycRFFT}")
    cycR = cycR.array
    cycRDF = pd.DataFrame(cycR.reshape((cycR.shape[0],cycR.shape[1])))

    M = cycRDF.to_numpy(float)

    if M.shape[0] == 11:
        responses = M
    else:
        responses = M.T

    A_vals = np.linspace(0,1,11)
    n_stim, n_trials = responses.shape

    # --------------------------------------------------------------
    # LOAD RF VECTOR
    # --------------------------------------------------------------
    rf_vec = summary[:,5].flatten()
    rf_vec = rf_vec[~np.isnan(rf_vec)]

    if rf_vec.size != 11:
        raise ValueError(f"RF file must contain 11 values, got {rf_vec.size}")

    RF = rf_vec

    # ==============================================================
    # SHOT-NOISE–CORRECTED CV AND FANO
    # ==============================================================
    shot_var_mean = inst_var_point / N_average

    def compute_CV_and_F(resp):

        # --------------------
        # FIX A (mean floor)
        # --------------------
        eps_mean = 1e-3
        means_raw = resp.mean(axis=1)
        means = np.maximum(means_raw, eps_mean)
        # --------------------

        var_meas = np.var(resp, axis=1, ddof=1)
        var_neural = np.maximum(var_meas - shot_var_mean, 0)

        CV_neural = np.sqrt(var_neural) / means
        F_tot = var_neural / means

        # contrasts 1..10
        F_fixed = float(np.clip(np.nanmean(F_tot[1:]), 0, 2))

        return CV_neural, F_tot, F_fixed

    CV_neural, F_tot, F_fixed = compute_CV_and_F(responses)

    # ==============================================================
    # MI PIPELINE
    # ==============================================================
    S = np.repeat(A_vals, n_trials)
    R = responses.flatten()

    def MI_KSG(x, y):
        x = x.reshape(-1,1)
        y = y.reshape(-1,1)
        xy = np.hstack((x,y))
        n = len(x)

        nn_xy = NearestNeighbors(n_neighbors=k).fit(xy)
        d,_ = nn_xy.kneighbors()
        eps = d[:,-1]

        nn_x = NearestNeighbors(n_neighbors=k).fit(x)
        nn_y = NearestNeighbors(n_neighbors=k).fit(y)

        nx = np.zeros(n,int)
        ny = np.zeros(n,int)

        for i in range(n):
            nx[i] = len(nn_x.radius_neighbors(x[i:i+1], eps[i], False)[0]) - 1
            ny[i] = len(nn_y.radius_neighbors(y[i:i+1], eps[i], False)[0]) - 1

        return (np.log(k)
                - np.mean(np.log(nx+1))
                - np.mean(np.log(ny+1))
                + np.log(n)) / np.log(2)

    base_std = np.sqrt(shot_var_mean)
    MI_means, noise_vars = [], []

    for s in noise_scales:
        tot_std = s * base_std
        add_std = np.sqrt(max(tot_std**2 - base_std**2, 0))
        R_s = R + rng.normal(0, add_std, R.size)
        MI_means.append(MI_KSG(S, R_s))
        noise_vars.append(tot_std**2)

    _, MI_corrected = np.polyfit(noise_vars, MI_means, 1)
    MI_measured = MI_means[0]

    # ==============================================================
    # DF_r SIMULATION
    # ==============================================================
    dt = 0.002
    T_base, T_stim = 10, 6
    f = 5
    tau = 0.05

    t = np.arange(0, T_base + T_stim, dt)
    L = max(int(5*tau/dt), 1)
    ker = np.exp(-np.arange(L)*dt/tau)
    ker /= (1/np.sqrt(1+(2*np.pi*f*tau)**2))

    idx_fit = np.arange(1,11)

    def simulate_CV_for_r0(r0, rng_local, reps):
        out = []

        for i,A in enumerate(A_vals):
            if A == 0:
                out.append(0.0)
                continue

            cvs = []

            for _ in range(reps):

                C = np.zeros_like(t)
                C[t>=T_base] = A*np.sin(2*np.pi*f*(t[t>=T_base] - T_base))

                C_eff = (1-RF[i])*C.clip(min=0) + (1+RF[i])*C.clip(max=0)
                r_t = r0*(1 - C_eff)
                lam = np.maximum(r_t*dt, 0)

                if np.isclose(F_fixed,1):
                    nves = rng_local.poisson(lam)
                elif F_fixed > 1:
                    ks = np.where(lam>0, lam/(F_fixed-1), 0)
                    lam_star = rng_local.gamma(ks, F_fixed-1)
                    nves = rng_local.poisson(lam_star)
                else:
                    aF = np.sqrt(F_fixed)
                    pois = rng_local.poisson(lam)
                    nves = (1-aF)*lam + aF*pois

                sig = np.convolve(amp_nominal*nves, ker, mode="full")[:len(t)]

                B0 = sig[(t>=T_base-8)&(t<T_base)].mean()

                df=[]

                for j in range(int(T_stim*f)):
                    m = (t>=T_base + j/f) & (t<T_base + (j+1)/f)
                    df.append(np.sum(np.abs(sig[m]-B0)*dt)/B0)

                df = np.asarray(df)
                cvs.append(df.std(ddof=1)/df.mean())

            out.append(np.nanmean(cvs))

        return np.asarray(out)

    # ==============================================================
    # FIT r0
    # ==============================================================
    def fit_r0(CV_target, reps, rng_local):

        def cost(r0):
            sim = simulate_CV_for_r0(r0, rng_local, reps)
            mse = np.nanmean((sim[idx_fit] - CV_target[idx_fit])**2)
            prior = max(0.0, (r0 - 100.0)/r0_prior_scale)
            return mse + prior

        res = minimize_scalar(cost, bounds=r0_bounds, method="bounded")
        return float(res.x)

    r0_best = fit_r0(CV_neural, sim_reps_per_A_fit, rng)
    CV_sim = simulate_CV_for_r0(r0_best, rng, sim_reps_per_A_fit)

    # ==============================================================
    # BOOTSTRAP CI
    # ==============================================================
    r0_boot = None
    r0_ci = None

    if n_boot > 0:
        rngb = np.random.default_rng(boot_seed)
        r0_boot = []

        for _ in range(n_boot):
            cols = rngb.integers(0,n_trials,n_trials)
            CV_b,_,_ = compute_CV_and_F(responses[:,cols])
            rng_local = np.random.default_rng(rngb.integers(0,2**32-1))
            r0b = fit_r0(CV_b, sim_reps_per_A_boot, rng_local)
            r0_boot.append(r0b)

        r0_boot = np.asarray(r0_boot)
        r0_ci = tuple(np.percentile(r0_boot,[2.5,97.5]))

    # --------------------------------------------------------------
    # RETURN
    # --------------------------------------------------------------
    igor.put(RF, model_outputName + "_RF")
    igor.put(F_fixed, model_outputName + "_FFix")

    igor.put(MI_measured, model_outputName + "_MI_M")
    igor.put(MI_corrected, model_outputName + "_MI_C")

    igor.put(r0_best, model_outputName + "_r0_best")
    igor.put(r0_ci, model_outputName + "_r0_ci")

    igor.put(CV_sim, model_outputName + "_CV_sim")
    igor.put(A_vals, model_outputName + "_A_vals")

    return "It works :D"
