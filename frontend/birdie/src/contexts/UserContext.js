import React, { createContext, useContext, useState, useEffect } from "react";
import jwtDecode from "jwt-decode";
import axios from "axios";

const userContext = createContext();

const defaultProfileData = {
    username: "",
    date_joined: "",
    profile_pic: "",
    following: "",
    follower: "",
};
function UserContextProvider({ children }) {
    const userTokensFromStorage = JSON.parse(localStorage.getItem("userTokens"));
    const [user, setUser] = useState(
        userTokensFromStorage && jwtDecode(userTokensFromStorage.access)
    );
    const [profileData, setProfileData] = useState(defaultProfileData);
    const [tokens, setTokens] = useState(userTokensFromStorage);
    const axiosInstance = axios.create({
        baseURL: "http://localhost:8000/api",
        headers: {
            Authorization: `Bearer ${tokens && tokens.access}`,
        },
    });

    const fetchUserData = async () => {
        console.log("fetching");
        const response = await axiosInstance.get("accounts/info/");
        setProfileData(response.data);
    };

    const login = (data, onfailure) => {
        axiosInstance
            .post("/accounts/token/", {
                username: data.username,
                password: data.password,
            })
            .then((response) => {
                data = response.data;
                if (response.status === 200) {
                    setUser(jwtDecode(data.access));
                    setTokens(data);
                    localStorage.setItem("userTokens", JSON.stringify(data));
                }
            })
            .catch((err) => {
                onfailure();
            });
    };

    const logout = () => {
        setUser(null);
        setTokens(null);
        setProfileData(defaultProfileData);
        localStorage.clear();
    };

    const authcontext = {
        user: user,
        login: login,
        axiosInstance: axiosInstance,
        logout: logout,
        profileData: profileData,
        setProfileData: setProfileData,
    };

    useEffect(() => {
        fetchUserData();
    }, [tokens]);

    return <userContext.Provider value={authcontext}>{children}</userContext.Provider>;
}

const useUserContext = () => {
    return useContext(userContext);
};

export default useUserContext;
export { userContext, UserContextProvider };
