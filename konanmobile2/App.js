// App.js
import React, { useContext } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { AuthProvider, AuthContext } from "./src/context/AuthContext";
import ChatScreen from "./src/screens/ChatScreen";
import LoginScreen from "./src/screens/LoginScreen";
import RegisterScreen from "./src/screens/RegisterScreen";
import SubscribeScreen from "./src/screens/SubscribeScreen"; // ← correspond exactement au fichier
import { TouchableOpacity, Text } from "react-native";

const Stack = createNativeStackNavigator();

function TextButton({ onPress, children }) {
  return (
    <TouchableOpacity onPress={onPress} style={{ marginRight: 12 }}>
      <Text style={{ color: "#10A37F", fontWeight: "600" }}>{children}</Text>
    </TouchableOpacity>
  );
}

function Router() {
  const { status, subscription } = useContext(AuthContext);
  const initial = status === "authenticated" ? "Chat" : "Login";

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName={initial}
        screenOptions={{
          headerStyle: { backgroundColor: "#0B0B0B" },
          headerTintColor: "#FFFFFF",
          contentStyle: { backgroundColor: "#0B0B0B" },
        }}
      >
        <Stack.Screen name="Login" component={LoginScreen} options={{ title: "KONAN" }} />
        <Stack.Screen name="Register" component={RegisterScreen} options={{ title: "Créer un compte" }} />
        <Stack.Screen
          name="Chat"
          component={ChatScreen}
          options={({ navigation }) => ({
            title: subscription === "premium" ? "KONAN • Premium" : "KONAN • Free",
            headerRight: () =>
              subscription === "premium" ? null : (
                <TextButton onPress={() => navigation.navigate("Subscribe")}>Premium</TextButton>
              ),
          })}
        />
        <Stack.Screen name="Subscribe" component={SubscribeScreen} options={{ title: "Abonnement" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}
