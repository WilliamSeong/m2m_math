import { Stack } from "expo-router";
import { Tabs } from 'expo-router';

export default function RootLayout() {
    return (
        <Stack>
            <Stack.Screen name="(tabs)" options={{ headerShown : false}} />
            <Stack.Screen name="components/studentProfile" />
        </Stack>
    )
}
